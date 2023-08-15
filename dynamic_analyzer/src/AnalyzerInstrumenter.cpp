#include "AnalyzerInstrumenter.hpp"

#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/Tooling/Transformer/RewriteRule.h>
#include <clang/Tooling/Transformer/Stencil.h>

#include <clang/AST/Decl.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>
#include <clang/Basic/TargetOptions.h>
#include <clang/Tooling/CommonOptionsParser.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Tooling/Transformer/MatchConsumer.h>

#include <sstream>
#include <string>
#include <regex>
#include <iostream>

using namespace clang;
using namespace ast_matchers;
using namespace transformer;

namespace analyzer {

namespace {

/* Self-defined computations/actions */

class InstrumentSiteAction : public MatchComputation<std::string> {
  public:
    InstrumentSiteAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const FunctionDecl *F = mResult.Nodes.getNodeAs<clang::FunctionDecl>("function");
        const Expr *E = mResult.Nodes.getNodeAs<clang::Expr>("expr");
        std::string typeStr = E->getType().getAsString();

        auto SR = CharSourceRange::getTokenRange(E->getSourceRange());
        auto exprStr = Lexer::getSourceText(SR, *mResult.SourceManager, mResult.Context->getLangOpts()).str();
        
        Result->append(";\n/*I:INSERTION:");
        Result->append(F->getNameAsString() + ":"); // function
        Result->append(typeStr + ":"); // type of expr
        Result->append(exprStr + ":"); // expr
        Result->append("ID" + std::to_string(instr_id++));
        Result->append("*/\n");
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }

    static int instr_id;
};

int InstrumentSiteAction::instr_id = 0;

class GlobalVarAction : public MatchComputation<std::string> {
  public:
    GlobalVarAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const FunctionDecl *F = mResult.Nodes.getNodeAs<clang::FunctionDecl>("function");
        const VarDecl *VD = mResult.Nodes.getNodeAs<clang::VarDecl>("global");
        std::string typeStr = VD->getType().getAsString();

        Result->append("\n/*I:GLOBAL:");
        Result->append(typeStr + ":"); // type of global
        Result->append(VD->getNameAsString()); // global
        Result->append("*/\n");
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
};

class LocalVarAction : public MatchComputation<std::string> {
  public:
    LocalVarAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const FunctionDecl *F = mResult.Nodes.getNodeAs<clang::FunctionDecl>("function");
        const VarDecl *VD = mResult.Nodes.getNodeAs<clang::VarDecl>("var");
        std::string typeStr = VD->getType().getAsString();

        Result->append("\n/*I:LOCAL:");
        Result->append(typeStr + ":"); // type of global
        Result->append(VD->getNameAsString() + ":"); // global
        Result->append("ID" + std::to_string(instr_id++));
        Result->append("*/\n");
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }

    static int instr_id;
};
int LocalVarAction::instr_id = 0;

class LogBraceAction : public MatchComputation<std::string> {
  public:
    LogBraceAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {

        char out_char[100];
        snprintf(out_char, sizeof(out_char), "\n/*I:ID%d:BRACESTART:*/\n", instr_id);
        instr_id++;
        std::string out_str(out_char);
        
        Result->append(out_str);
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }

    static int instr_id;
};

int LogBraceAction::instr_id = 0;



auto stmtMatcher = allOf(
                    isExpansionInMainFile(), 
                    unless(anyOf(declStmt(), ifStmt(), forStmt(), switchStmt(), caseStmt(), defaultStmt(), doStmt(), whileStmt(), returnStmt())), // donot instrument 
                    unless(hasAncestor(functionDecl(isMain()))), // donot instrument main function
                    hasAncestor(functionDecl().bind("function")),
                    hasParent(compoundStmt()));

// rule for logging arraySubscriptExpr
auto logArrayRule() {
    return makeRule(stmt(stmtMatcher,
                    forEachDescendant(arraySubscriptExpr(unless(hasAncestor(arraySubscriptExpr()))).bind("expr"))
                ).bind("stmt"), insertAfter(node("stmt"), std::make_unique<InstrumentSiteAction>()));
}

// rule for logging declRefExpr
auto logDeclRefRule() {
    return makeRule(stmt(stmtMatcher,
                    forEachDescendant(declRefExpr(unless(anyOf(hasAncestor(callExpr()), to(varDecl(hasParent(declStmt(hasParent(forStmt())))))))).bind("expr"))
                ).bind("stmt"), insertAfter(node("stmt"), std::make_unique<InstrumentSiteAction>()));
}

// rule for logging varDecl
auto logLocalVarRule() {
    return makeRule(varDecl(
                        isExpansionInMainFile(), 
                        hasLocalStorage(), 
                        unless(parmVarDecl()), 
                        unless(hasAncestor(functionDecl(isMain()))),
                        unless(hasParent(declStmt(hasParent(forStmt()))))
                    ).bind("var"),
                    insertAfter(node("var"), std::make_unique<LocalVarAction>()));
}

// rule for logging global vars
auto logGlobalVarRule() {
    return makeRule(
        translationUnitDecl(
            findAll(varDecl(isExpansionInMainFile(), hasGlobalStorage()).bind("global")),
            hasDescendant(functionDecl(
                isMain(),
                hasBody(compoundStmt(hasDescendant(stmt().bind("mainBody"))))
        ))),
        insertBefore(node("mainBody"), std::make_unique<GlobalVarAction>())
    );
}

// rule for logging braces
auto logBracesRule() {
    return makeRule(
            compoundStmt(
                isExpansionInMainFile(),
                unless(hasAncestor(functionDecl(isMain())))).bind("compound"),
            {insertBefore(node("compound"), std::make_unique<LogBraceAction>()),
            insertAfter(node("compound"), cat("\n/*I:ID:BRACEEND:*/\n"))});
}

/* Logging instrumentation sites: right before each statement */
class LogInstrumentSiteAction : public MatchComputation<std::string> {
  public:
    LogInstrumentSiteAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        std::string id_str = std::to_string(instr_id);
        Result->append("\n/*I:ID" + id_str + ":INSERTIONSITE:*/");
        Result->append("if (print_flag_inst[" + id_str+"]!=2) {");
        Result->append("printf(\"INST:" + id_str +"\\n\");");
        Result->append("print_flag_inst["+id_str + "]++;");
        Result->append("}\n");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }

    static int instr_id;
};

int LogInstrumentSiteAction::instr_id = 0;

auto LogInstrumentSiteRule() {

    auto stmtMatcher = allOf(
                    isExpansionInMainFile(), 
                    unless(hasAncestor(functionDecl(isMain()))), 
                    // unless(anyOf(ifStmt(), forStmt(), switchStmt(), caseStmt(), defaultStmt(), doStmt(), whileStmt())), // donot instrument 
                    hasParent(compoundStmt()));
    return makeRule(stmt(stmtMatcher).bind("stmt"), insertBefore(node("stmt"), std::make_unique<LogInstrumentSiteAction>()));
}

/* Logging function entering */
class LogFuncEntAction : public MatchComputation<std::string> {
  public:
    LogFuncEntAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        Result->append("/*I:ID"+std::to_string(instr_id)+":FUNCTIONENTER");
        Result->append(":*/\n");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
    static int instr_id;
};
int LogFuncEntAction::instr_id = 0;

auto LogFuncEntRule() {
    auto funcDeclMatcher = functionDecl(
        isExpansionInMainFile(),
        unless(isMain()),
        hasDescendant(stmt(hasParent(compoundStmt())).bind("stmt"))
    );
    return makeRule(funcDeclMatcher, insertBefore(node("stmt"), std::make_unique<LogFuncEntAction>()));
}


/* Logging variable declaration */
class LogVarDeclAction : public MatchComputation<std::string> {
  public:
    LogVarDeclAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const NamedDecl *var = mResult.Nodes.getNodeAs<clang::NamedDecl>("var");
        const ValueDecl *var_type = mResult.Nodes.getNodeAs<clang::ValueDecl>("var");
        std::string typeStr = var_type->getType().getAsString();
        typeStr = std::regex_replace(typeStr, std::regex("volatile"), "");
        if (/*typeStr.find("struct") != -1 ||*/ typeStr.find("union") != -1 || typeStr.find("const") != -1) {
            return llvm::Error::success();
        }
        std::string id_str = std::to_string(instr_id);
        Result->append("/*I:ID");
        Result->append(id_str);
        Result->append(":VARDECL:");
        Result->append(typeStr + ":");
        Result->append(var->getNameAsString());
        Result->append(":*/\n");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
    static int instr_id;
};
int LogVarDeclAction::instr_id = 0;

auto LogVarDeclRule() {
    auto varDeclMatcher = varDecl(
        isExpansionInMainFile(),
        hasLocalStorage(),
        hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
    ).bind("var");
    return makeRule(varDeclMatcher, insertBefore(node("stmt"), std::make_unique<LogVarDeclAction>()));
}

/* Logging array usage: right before each array usage except for declarations */
class LogVarArrayAction : public MatchComputation<std::string> {
  public:
    LogVarArrayAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const NamedDecl *var = mResult.Nodes.getNodeAs<clang::NamedDecl>("var");
        const ValueDecl *var_type = mResult.Nodes.getNodeAs<clang::ValueDecl>("var");
        const NamedDecl *idx = mResult.Nodes.getNodeAs<clang::NamedDecl>("idx");
        const ValueDecl *type = mResult.Nodes.getNodeAs<clang::ValueDecl>("var");
        std::string typeStr = var_type->getType().getAsString();
        typeStr = std::regex_replace(typeStr, std::regex("volatile"), "");
        if (typeStr.find("struct") != -1 || typeStr.find("union") != -1 || typeStr.find("const") != -1) {
            return llvm::Error::success();
        }
        Result->append("/*I:ID");
        Result->append(std::to_string(instr_id));
        Result->append(":VARREF_ARRAY:");
        Result->append(typeStr + ":");
        Result->append(var->getNameAsString() + ":");
        Result->append(idx->getNameAsString());
        Result->append(":*/\n");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
    static int instr_id;
};
int LogVarArrayAction::instr_id = 0;

auto LogVarArrayRule() {
    auto arrayMatcher = arraySubscriptExpr(
        isExpansionInMainFile(), 
        // unless(hasAncestor(arraySubscriptExpr())), 
        unless(hasAncestor(functionDecl(isMain()))), 
        unless(hasAncestor(varDecl())),
        unless(hasAncestor(binaryOperator(hasOperatorName("||")))),
        hasBase(hasDescendant(declRefExpr(hasDeclaration(varDecl().bind("var"))))), 
        hasIndex(expr(hasDescendant(declRefExpr(hasDeclaration(varDecl().bind("idx")))))),
        hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
    );
    return makeRule(arrayMatcher, insertBefore(node("stmt"), std::make_unique<LogVarArrayAction>()));
}

/* Logging pointer usage: right before each pointer usage except for declarations */
class LogVarPointerAction : public MatchComputation<std::string> {
  public:
    LogVarPointerAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const Expr *var = mResult.Nodes.getNodeAs<clang::Expr>("var");
        std::string typeStr = var->getType().getAsString();
        typeStr = std::regex_replace(typeStr, std::regex("volatile"), "");
        if (/*typeStr.find("struct") != -1 || */typeStr.find("union") != -1 || typeStr.find("const") != -1) {
            return llvm::Error::success();
        }
        const Expr *assign = mResult.Nodes.getNodeAs<clang::Expr>("assign");
        if (assign) {
            std::string id_str = std::to_string(instr_id);
            std::string expr = getExprAsText(var, *mResult.SourceManager, mResult.Context->getLangOpts());
            Result->append("/*I:ID");
            Result->append(std::to_string(instr_id));
            Result->append(":VARREF_ASSIGN:");
            Result->append(typeStr + ":");
            Result->append(expr);
            Result->append(":*/\n");
            instr_id++;
            return llvm::Error::success();
        }
        std::string id_str = std::to_string(instr_id);
        std::string expr = getExprAsText(var, *mResult.SourceManager, mResult.Context->getLangOpts());
        Result->append("/*I:ID");
        Result->append(std::to_string(instr_id));
        Result->append(":VARREF_POINTER:");
        Result->append(typeStr + ":");
        Result->append(expr);
        Result->append(":*/");
        Result->append("if (print_flag_ptr[" + id_str+"]!=2) {");
        Result->append("printf(\"PTR:" + id_str + ":%p" +"\\n\"," + expr +");");
        Result->append("print_flag_ptr["+id_str + "]++;");
        Result->append("}\n");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
    static int instr_id;
    static std::string getExprAsText(const Expr *E, const SourceManager &SM, const LangOptions &lp) {
        auto SR = CharSourceRange::getTokenRange(E->getSourceRange());
        return Lexer::getSourceText(SR, SM, lp).str();
    }
};
int LogVarPointerAction::instr_id = 0;

auto LogVarPointerRule() {
    auto pointerMatcher = declRefExpr(
            isExpansionInMainFile(),
            unless(hasAncestor(functionDecl(isMain()))),
            unless(hasParent((binaryOperator(hasOperatorName("="))))),
            unless(hasAncestor(binaryOperator(hasOperatorName("||")))),
            unless(hasDeclaration(parmVarDecl())), // do not mutate pointer in function paramters
            unless(hasAncestor(callExpr())), // don't match anything in a function call
            anyOf(hasAncestor((unaryOperator(hasOperatorName("*")))), hasAncestor(arraySubscriptExpr())),
            // unless(hasType(arrayType())), 
            unless(hasAncestor(varDecl())), 
            unless(hasAncestor(unaryOperator(hasOperatorName("++")))), 
            unless(hasAncestor(unaryOperator(hasOperatorName("--")))), 
            unless(hasAncestor(unaryOperator(hasOperatorName("&")))), 
            anyOf(hasType(pointerType()), hasType(arrayType())),
            unless(hasType(decayedType())),
            hasDeclaration(varDecl()),
            hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
            ).bind("var");
    // match pointer assignment
    auto pointerAssignMatcher = declRefExpr(
            isExpansionInMainFile(),
            unless(hasAncestor(functionDecl(isMain()))),
            hasParent((binaryOperator(hasOperatorName("="))).bind("assign")),
            unless(hasAncestor(varDecl())), 
            anyOf(hasType(pointerType()), hasType(arrayType())),
            unless(hasType(decayedType())),
            hasDeclaration(varDecl()),
            hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
            ).bind("var");
    auto arrayMatcher = arraySubscriptExpr(
            isExpansionInMainFile(),
            unless(hasAncestor(functionDecl(isMain()))),
            unless(hasParent((binaryOperator(hasOperatorName("="))))),
            unless(hasAncestor(callExpr())), // don't match anything in a function call
            // unless(hasDeclaration(parmVarDecl())), // do not mutate pointer in function paramters
            // unless(hasType(arrayType())), 
            // unless(hasAncestor(varDecl())), 
            // unless(hasAncestor(unaryOperator(hasOperatorName("++")))), 
            // unless(hasAncestor(unaryOperator(hasOperatorName("--")))), 
            unless(hasAncestor(unaryOperator(hasOperatorName("&")))), 
            anyOf(hasType(pointerType()), hasType(arrayType())),
            // unless(hasType(decayedType())),
            // hasDeclaration(varDecl().bind("var")),
            hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
            ).bind("var");
    // match array assignment
    auto arrayAssignMatcher = arraySubscriptExpr(
            isExpansionInMainFile(),
            unless(hasAncestor(functionDecl(isMain()))),
            hasParent((binaryOperator(hasOperatorName("="))).bind("assign")),
            unless(hasAncestor(varDecl())), 
            anyOf(hasType(pointerType()), hasType(arrayType())),
            hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
            ).bind("var");
    // return makeRule(arrayMatcher, insertBefore(node("stmt"), std::make_unique<LogVarPointerAction>()));
    return applyFirst({
        makeRule(pointerMatcher, insertBefore(node("stmt"), std::make_unique<LogVarPointerAction>())),
        makeRule(pointerAssignMatcher, insertBefore(node("stmt"), std::make_unique<LogVarPointerAction>())),
        makeRule(arrayMatcher, insertBefore(node("stmt"), std::make_unique<LogVarPointerAction>())),
        makeRule(arrayAssignMatcher, insertBefore(node("stmt"), std::make_unique<LogVarPointerAction>()))
    });
}


/* Logging memory usage: right before each pointer usage except for declarations */
class LogVarMemoryAction : public MatchComputation<std::string> {
  public:
    LogVarMemoryAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const Expr *func_call = mResult.Nodes.getNodeAs<clang::Expr>("func_call");
        if (func_call) {
            std::string funcCallStr = getExprAsText(func_call, *mResult.SourceManager, mResult.Context->getLangOpts());
            if (funcCallStr.find("safe_") == -1) {
                return llvm::Error::success();
            }
        }
        const Expr *var = mResult.Nodes.getNodeAs<clang::Expr>("var");
        bool is_member = false;
        if (!var) {
            var = mResult.Nodes.getNodeAs<clang::Expr>("member");
            is_member = true;
        }
        std::string typeStr = var->getType().getAsString();
        typeStr = std::regex_replace(typeStr, std::regex("volatile"), "");
        if (/*typeStr.find("struct") != -1 || */typeStr.find("union") != -1 || typeStr.find("const") != -1) {
            return llvm::Error::success();
        }
        std::string exprStr = getExprAsText(var, *mResult.SourceManager, mResult.Context->getLangOpts());
        if (exprStr.find("_MUT") == -1) { // pointers that are not selected by ArrayIndexAdd
            return llvm::Error::success();
        }
        std::string expr_address;
        if (is_member) {
            expr_address = exprStr;
            if (typeStr.find("*") == -1) { //we want member pointer, e.g., a->x, not member expr pointer, e.g., a.x
                return llvm::Error::success();
            }
        } else {
            expr_address = "&(" + exprStr + ")";
        }
        std::string id_str = std::to_string(instr_id);
        Result->append("/*I:ID");
        Result->append(id_str);
        Result->append(":VARREF_MEMORY:");
        Result->append(typeStr + ":" + exprStr + ":*/");
        Result->append("if (print_flag_mem[" + id_str+"]!=2) {");
        Result->append("printf(\"MEM:" + id_str + ":%p:%p\\n\"," + expr_address + "," + "(" + expr_address + ")+1" + ");");
        Result->append("print_flag_mem["+id_str + "]++;");
        Result->append("}\n");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
    static int instr_id;
    static std::string getExprAsText(const Expr *E, const SourceManager &SM, const LangOptions &lp) {
        auto SR = CharSourceRange::getTokenRange(E->getSourceRange());
        return Lexer::getSourceText(SR, SM, lp).str();
    }
};
int LogVarMemoryAction::instr_id = 0;


class LogVarDeclMemoryAction : public MatchComputation<std::string> {
  public:
    LogVarDeclMemoryAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const NamedDecl *var = mResult.Nodes.getNodeAs<clang::NamedDecl>("local_pointer");
        const ValueDecl *var_type = mResult.Nodes.getNodeAs<clang::ValueDecl>("local_pointer");
        bool is_pointer = true;
        bool is_global = false;
        if (!var) {
            var = mResult.Nodes.getNodeAs<clang::NamedDecl>("global_non_pointer");
            var_type = mResult.Nodes.getNodeAs<clang::ValueDecl>("global_non_pointer");
            is_pointer = false;
            is_global = true;
        }
        if (!var) {
            var = mResult.Nodes.getNodeAs<clang::NamedDecl>("global_pointer");
            var_type = mResult.Nodes.getNodeAs<clang::ValueDecl>("global_pointer");
            is_pointer = true;
            is_global = true;
        }
        if (!var) {
            return llvm::Error::success();;
        }
        std::string var_address = "&(" + var->getNameAsString() + ")";;
        // if (is_pointer) {
        //     var_address = var->getNameAsString();
        // } else {
        //     var_address = "&(" + var->getNameAsString() + ")";
        // }
        std::string var_scope;
        if (is_global) {
            var_scope = "GLOBAL";
        } else {
            var_scope = "LOCAL";
        }
        std::string typeStr = var_type->getType().getAsString();
        typeStr = std::regex_replace(typeStr, std::regex("volatile"), "");
        // if (/*typeStr.find("struct") != -1 ||*/ typeStr.find("union") != -1 /*|| typeStr.find("const") != -1*/) {
        //     return llvm::Error::success();
        // }
        std::string id_str = std::to_string(instr_id);
        Result->append("\n/*I:ID");
        Result->append(id_str);
        Result->append(":VARDECL:");
        Result->append(typeStr + ":");
        Result->append(var->getNameAsString());
        Result->append(":*/");
        Result->append("if (!print_flag_var[" + id_str+"]) {");
        Result->append("printf(\""+var_scope+":" + id_str + ":%p:%d\\n\"," + var_address + ",sizeof(" + typeStr + "));");
        // Result->append("print_flag_var["+id_str + "]=1;"); // one local variable may be re-allocated when call the function more than once.
        Result->append("}\n");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
    static int instr_id;
};
int LogVarDeclMemoryAction::instr_id = 0;

auto LogVarMemoryRule() {
    auto pointerMatcher = unaryOperator(
            isExpansionInMainFile(),
            unless(hasAncestor(functionDecl(isMain()))),
            unless(hasAncestor(varDecl())), 
            unless(hasAncestor(binaryOperator(hasOperatorName("||")))),
            unless(hasAncestor(callExpr())), // don't match anything in a function call // don't match anything in a function call
            hasAnyOperatorName("*"),
            hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
            ).bind("var");
    auto memberExprMatcher = memberExpr(
            isExpansionInMainFile(),
            unless(hasAncestor(functionDecl(isMain()))),
            unless(hasAncestor(binaryOperator(hasOperatorName("||")))),
            unless(hasAncestor(varDecl())), 
            unless(hasAncestor(callExpr())), // don't match anything in a function call
            hasDescendant(expr().bind("member")),
            hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
            );
    auto arrayMatcher = arraySubscriptExpr(
            isExpansionInMainFile(),
            unless(hasAncestor(functionDecl(isMain()))),
            unless(hasAncestor(arraySubscriptExpr())),
            unless(hasAncestor(binaryOperator(hasOperatorName("||")))),
            unless(hasAncestor(callExpr())), // don't match anything in a function call
            unless(hasAncestor(varDecl())), 
            unless(hasAncestor(unaryOperator(hasOperatorName("&")))), 
            hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
            ).bind("var");
    auto localVarDeclMatcher = varDecl(
            isExpansionInMainFile(),
            unless(hasAncestor(functionDecl(isMain()))),
            unless(hasAncestor(binaryOperator(hasOperatorName("||")))),
            hasLocalStorage(),
            // anyOf(hasType(pointerType()), hasType(arrayType())),
            unless(hasParent(declStmt(hasParent(forStmt())))),
            hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
            ).bind("local_pointer");
    auto globalVarDeclPointerMatcher = varDecl(
            isExpansionInMainFile(),
            unless(hasAncestor(functionDecl(isMain()))),
            hasGlobalStorage(),
            // anyOf(hasType(pointerType()), hasType(arrayType())),
            hasParent(translationUnitDecl(hasDescendant(functionDecl(isMain(), hasBody(compoundStmt(has(stmt().bind("stmt"))))))))
            ).bind("global_pointer");
    auto globalVarDeclNonPointerMatcher = varDecl(
            isExpansionInMainFile(),
            unless(hasAncestor(functionDecl(isMain()))),
            hasGlobalStorage(),
            unless(hasType(pointerType())),
            unless(hasType(arrayType())),
            hasParent(translationUnitDecl(hasDescendant(functionDecl(isMain(), hasBody(compoundStmt(has(stmt().bind("stmt"))))))))
            ).bind("global_non_pointer");
    return applyFirst({
        makeRule(pointerMatcher, insertBefore(node("stmt"), std::make_unique<LogVarMemoryAction>())),
        makeRule(memberExprMatcher, insertBefore(node("stmt"), std::make_unique<LogVarMemoryAction>())),
        makeRule(arrayMatcher, insertBefore(node("stmt"), std::make_unique<LogVarMemoryAction>())),
        makeRule(localVarDeclMatcher, insertAfter(node("stmt"), std::make_unique<LogVarDeclMemoryAction>())),
        makeRule(globalVarDeclPointerMatcher, insertBefore(node("stmt"), std::make_unique<LogVarDeclMemoryAction>()))
        // makeRule(globalVarDeclNonPointerMatcher, insertBefore(node("stmt"), std::make_unique<LogVarDeclMemoryAction>()))
    });
}

/* Logging pointer index usage: right before each pointer usage except for declarations */
class LogVarPointerIndexAction : public MatchComputation<std::string> {
  public:
    LogVarPointerIndexAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const NamedDecl *var = mResult.Nodes.getNodeAs<clang::NamedDecl>("idx");
        std::string var_str = var->getNameAsString();
        if (var_str.find("MUT_PTR") == -1) {
            return llvm::Error::success();
        }
        Result->append("/*I:ID");
        Result->append(std::to_string(instr_id));
        Result->append(":VARREF_POINTERINDEX:int:");
        Result->append(var->getNameAsString());
        Result->append(":*/\n");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
    static int instr_id;
};
int LogVarPointerIndexAction::instr_id = 0;

auto LogVarPointerIndexRule() {
    auto pointerIndexMatcher = binaryOperator(
        hasOperatorName("+"),
        unless(hasAncestor(binaryOperator(hasOperatorName("||")))),
        hasRHS(ignoringParenImpCasts(declRefExpr(hasDeclaration(varDecl().bind("idx"))))),
        hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
    );
    return makeRule(pointerIndexMatcher, insertBefore(node("stmt"), std::make_unique<LogVarPointerIndexAction>()));
}

/* Logging integer usage: right before each integer usage except for declarations */
class LogIntegerAction : public MatchComputation<std::string> {
public:
    LogIntegerAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const Expr *operand = mResult.Nodes.getNodeAs<clang::Expr>("operand");
        std::string typeStr = operand->getType().getAsString();
        typeStr = std::regex_replace(typeStr, std::regex("volatile"), "");
        if (typeStr.find("struct") != -1 || typeStr.find("union") != -1 || typeStr.find("const") != -1) {
            return llvm::Error::success();
        }
        std::string operand_str = getExprAsText(operand, *mResult.SourceManager, mResult.Context->getLangOpts());
        if (operand_str.find("MUT_") != -1) {
            return llvm::Error::success();
        }
        Result->append("/*I:ID");
        Result->append(std::to_string(instr_id));
        Result->append(":VARREF_INTEGER:");
        Result->append(typeStr+":");
        Result->append(operand_str);
        Result->append(":*/\n");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
    static int instr_id;
    static std::string getExprAsText(const Expr *E, const SourceManager &SM, const LangOptions &lp) {
        auto SR = CharSourceRange::getTokenRange(E->getSourceRange());
        return Lexer::getSourceText(SR, SM, lp).str();
    }
};
int LogIntegerAction::instr_id = 0;

auto LogIntegerRule() {

    auto targetExpr = expr(
        unless(hasAncestor(arraySubscriptExpr())), 
        anyOf(declRefExpr(), arraySubscriptExpr(), memberExpr(), unaryOperator(hasOperatorName("*")))
    );

    auto operandMather = binaryOperator(
        isExpansionInMainFile(),
        hasAnyOperatorName("+", "+=", "-", "-=", "*", "*=", "/", "/=", "<<", "<<=", ">>", ">>="),
        unless(hasParent(forStmt())), // avoid matching for increment statement
        unless(hasAncestor(callExpr())), // don't match anything in a function call
        eachOf(
        hasLHS(ignoringParenImpCasts(targetExpr.bind("operand"))),
        hasLHS(ignoringParenImpCasts((ignoringParenCasts(targetExpr.bind("operand"))))),
        hasRHS(ignoringParenImpCasts((ignoringParenCasts(targetExpr.bind("operand"))))),
        hasRHS(ignoringParenImpCasts(targetExpr.bind("operand")))
        ),
        hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
    );

    auto castMather = cStyleCastExpr(
        isExpansionInMainFile(),
        hasDescendant(targetExpr.bind("operand")),
        hasAncestor(binaryOperator(unless(isAssignmentOperator()))),
        hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
    );


    return applyFirst({
        makeRule(operandMather, insertBefore(node("stmt"), std::make_unique<LogIntegerAction>()))
        // makeRule(castMather, insertBefore(node("stmt"), std::make_unique<LogIntegerAction>()))
    });
}

/* Logging integer usage: right before each integer usage except for declarations */
class LogIntegerOpAction : public MatchComputation<std::string> {
public:
    LogIntegerOpAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const Expr *lhs = mResult.Nodes.getNodeAs<clang::Expr>("lhs");
        const Expr *rhs = mResult.Nodes.getNodeAs<clang::Expr>("rhs");
        const BinaryOperator *opcode = mResult.Nodes.getNodeAs<clang::BinaryOperator>("operator");
        std::string lhs_typeStr = lhs->getType().getAsString();
        lhs_typeStr = std::regex_replace(lhs_typeStr, std::regex("volatile"), "");
        if (lhs_typeStr.find("struct") != -1 || lhs_typeStr.find("union") != -1 || lhs_typeStr.find("const") != -1 || lhs_typeStr.find("*") != -1 || lhs_typeStr.find("[") != -1) {
            return llvm::Error::success();
        }
        std::string lhs_type_print;
        if (lhs_typeStr.find("uint") != -1 || lhs_typeStr.find("unsigned") != -1) {
            lhs_type_print = "%llu";
        } else {
            lhs_type_print = "%lld";
        }
        std::string rhs_typeStr = rhs->getType().getAsString();
        rhs_typeStr = std::regex_replace(rhs_typeStr, std::regex("volatile"), "");
        if (rhs_typeStr.find("struct") != -1 || rhs_typeStr.find("union") != -1 || rhs_typeStr.find("const") != -1 || rhs_typeStr.find("*") != -1 || rhs_typeStr.find("[") != -1) {
            return llvm::Error::success();
        }
        std::string rhs_type_print;
        if (rhs_typeStr.find("uint") != -1 || rhs_typeStr.find("unsigned") != -1) {
            rhs_type_print = "%llu";
        } else {
            rhs_type_print = "%lld";
        }
        std::string lhs_str = getExprAsText(lhs, *mResult.SourceManager, mResult.Context->getLangOpts());
        if (lhs_str.find("MUT_") != -1) {
            return llvm::Error::success();
        }
        lhs_str = std::regex_replace(lhs_str, std::regex("\\+\\+"), "");
        lhs_str = std::regex_replace(lhs_str, std::regex("--"), "");
        std::string rhs_str = getExprAsText(rhs, *mResult.SourceManager, mResult.Context->getLangOpts());
        if (rhs_str.find("MUT_") != -1) {
            return llvm::Error::success();
        }
        rhs_str = std::regex_replace(rhs_str, std::regex("\\+\\+"), "");
        rhs_str = std::regex_replace(rhs_str, std::regex("--"), "");
        Result->append("/*I:ID");
        Result->append(std::to_string(instr_id));
        Result->append(":VARREF_INTEGER:");
        Result->append(lhs_typeStr+":"+lhs_str+":");
        Result->append(rhs_typeStr+":"+rhs_str+":");
        Result->append(opcode->getOpcodeStr().str() + ":*/");

        std::string id_str = std::to_string(instr_id);
        if (lhs_type_print=="%lld") {
            lhs_str = "(long long)" + lhs_str;
        } else {
            lhs_str = "(unsigned long long)" + lhs_str;
        }
        if (rhs_type_print=="%lld") {
            rhs_str = "(long long)" + rhs_str;
        } else {
            rhs_str = "(unsigned long long)" + rhs_str;
        }
        Result->append("if (print_flag_int[" + id_str+"]!=2) {");
        Result->append("printf(\"INT:" + id_str +":" + lhs_type_print + ":" + rhs_type_print + "\\n\"," + lhs_str + "," + rhs_str + ");");
        Result->append("print_flag_int["+id_str + "]++;");
        Result->append("}\n");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
    static int instr_id;
    static std::string getExprAsText(const Expr *E, const SourceManager &SM, const LangOptions &lp) {
        auto SR = CharSourceRange::getTokenRange(E->getSourceRange());
        return Lexer::getSourceText(SR, SM, lp).str();
    }
};
int LogIntegerOpAction::instr_id = 0;

auto LogIntegerOpRule() {

    auto operandMather = 
            binaryOperator(
                isExpansionInMainFile(),
                unless(hasAncestor(binaryOperator(hasOperatorName("||")))),
                hasAnyOperatorName("+", "-", "*", "<<", ">>"),
                unless(hasParent(forStmt())), // avoid matching for increment statement
                unless(hasAncestor(callExpr())), // don't match anything in a function call 
                hasLHS(expr().bind("lhs")),
                hasRHS(expr().bind("rhs")),
                hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
            ).bind("operator");

    return makeRule(operandMather, insertBefore(node("stmt"), std::make_unique<LogIntegerOpAction>()));
}

auto LogVarDividerOpRule() {

    auto operandMather = 
            binaryOperator(
                isExpansionInMainFile(),
                unless(hasAncestor(binaryOperator(hasOperatorName("||")))),
                hasAnyOperatorName("/", "%"),
                unless(hasParent(forStmt())), // avoid matching for increment statement
                hasLHS(expr().bind("lhs")),
                hasRHS(expr().bind("rhs")),
                hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
            ).bind("operator");

    return makeRule(operandMather, insertBefore(node("stmt"), std::make_unique<LogIntegerOpAction>()));
}

/*
    Match expressions with integer types
*/
class LogInitBranchAction : public MatchComputation<std::string> {
public:
    LogInitBranchAction() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const Expr *expr = mResult.Nodes.getNodeAs<clang::Expr>("expr");
        std::string expr_str = getExprAsText(expr, *mResult.SourceManager, mResult.Context->getLangOpts());
        std::string typeStr = expr->getType().getAsString();
        typeStr = std::regex_replace(typeStr, std::regex("volatile"), "");
        Result->append("/*I:ID");
        Result->append(std::to_string(instr_id));
        Result->append(":VARREF_INIT:");
        Result->append(typeStr+":");
        Result->append(expr_str);
        Result->append(":*/\n");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
    static int instr_id;
    static std::string getExprAsText(const Expr *E, const SourceManager &SM, const LangOptions &lp) {
        auto SR = CharSourceRange::getTokenRange(E->getSourceRange());
        return Lexer::getSourceText(SR, SM, lp).str();
    }
};
int LogInitBranchAction::instr_id = 0;

auto LogInitBranchRule() {
    auto typeMatcher = anyOf(
                    hasType(asString("int8_t")), 
                    hasType(asString("uint8_t")), 
                    hasType(asString("int16_t")), 
                    hasType(asString("uint16_t")), 
                    hasType(asString("int32_t")), 
                    hasType(asString("uint32_t")), 
                    hasType(asString("int64_t")),
                    hasType(asString("uint64_t")));
    auto exprMatcher = ifStmt(
        isExpansionInMainFile(),
        hasCondition(forEachDescendant(
            expr(
                unless((implicitCastExpr())),
                unless(anyOf(
                    hasAncestor(binaryOperator(hasAnyOperatorName("||", "|", "=","|=", "&=", "<", "<=", ">", ">=", ","))),
                    hasAncestor(unaryOperator(hasOperatorName("&")))
                )),
                unless(hasAncestor(callExpr())), // don't match anything in a function call 
                unless(hasAncestor(arraySubscriptExpr())),
                typeMatcher
            ).bind("expr")
        ))
    ).bind("stmt");
    return makeRule(exprMatcher, {
                // insertBefore(node("expr"), cat("/*initS*/")),
                // insertAfter(node("expr"), cat("/*initE*/")),
                insertBefore(node("stmt"), std::make_unique<LogInitBranchAction>())
            });
}

/* 
    AddGlobalMacro
*/
class AddGlobalMacro : public MatchComputation<std::string> {
  public:
    AddGlobalMacro() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &,
                     std::string *Result) const override {
        Result->append("/*I::*/ int print_flag_inst[" + std::to_string(LogInstrumentSiteAction::instr_id) + "];\n");
        Result->append("/*I::*/ int print_flag_int[" + std::to_string(LogIntegerOpAction::instr_id) + "];\n");
        Result->append("/*I::*/ int print_flag_mem[" + std::to_string(LogVarMemoryAction::instr_id) + "];\n");
        Result->append("/*I::*/ int print_flag_var[" + std::to_string(LogVarDeclMemoryAction::instr_id) + "];\n");
        Result->append("/*I::*/ int print_flag_ptr[" + std::to_string(LogVarPointerAction::instr_id) + "];\n");
        return llvm::Error::success();
    }

    std::string toString() const override {
        return "AddGlobalMacroError\n";
    }
};

auto addGlobalMacroRule() {
    return makeRule(functionDecl(
        isExpansionInMainFile(),
        isMain()
        ).bind("main"),
        insertAfter(ruleactioncallback::startOfFile("main"), 
        std::make_unique<AddGlobalMacro>()));
}

auto allRules() {
    return applyFirst({
        logBracesRule(),
        // logGlobalVarRule(),
        // logLocalVarRule(),
        // logArrayRule(),
        // logDeclRefRule(),

        LogVarDeclRule(),
        // LogVarArrayRule(),
        // LogVarPointerRule(),
        // LogVarPointerIndexRule(),
        // LogIntegerRule(),
        LogIntegerOpRule(),
        // LogInstrumentSiteRule(),
        LogFuncEntRule(),
        addGlobalMacroRule(),
    });
}

} // namespace

AnalyzerInstrumenter::AnalyzerInstrumenter(
    std::map<std::string, clang::tooling::Replacements> &FileToReplacements, ToolMode mode)
    :  FileToReplacements{FileToReplacements} {

    Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          logBracesRule(), FileToReplacements, FileToNumberValueTrackers});
    Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          LogVarDeclRule(), FileToReplacements, FileToNumberValueTrackers});
    Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          LogInstrumentSiteRule(), FileToReplacements, FileToNumberValueTrackers});
    switch (mode)
    {
    case ToolMode::ArrayIndex:
        Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          LogVarArrayRule(), FileToReplacements, FileToNumberValueTrackers});
        break;
    case ToolMode::PointerIndex:
        Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          LogVarPointerIndexRule(), FileToReplacements, FileToNumberValueTrackers});
        break;
    case ToolMode::ArrayPointerIndex:
        Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          LogVarArrayRule(), FileToReplacements, FileToNumberValueTrackers});
        Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          LogVarPointerIndexRule(), FileToReplacements, FileToNumberValueTrackers});
        break;
    case ToolMode::Memory:
        Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          LogVarMemoryRule(), FileToReplacements, FileToNumberValueTrackers});
        break;
    case ToolMode::Pointer:
        Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          LogVarPointerRule(), FileToReplacements, FileToNumberValueTrackers});
        break;
    case ToolMode::Integer:
        Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          LogIntegerOpRule(), FileToReplacements, FileToNumberValueTrackers});
        break;
    case ToolMode::Divider:
        Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          LogVarDividerOpRule(), FileToReplacements, FileToNumberValueTrackers});
        break;
    case ToolMode::Init:
        Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          LogInitBranchRule(), FileToReplacements, FileToNumberValueTrackers});
        break;
    default:
        break;
    }

    // Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
    //       LogInstrumentSiteRule(), FileToReplacements, FileToNumberValueTrackers});
    Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          LogFuncEntRule(), FileToReplacements, FileToNumberValueTrackers});
    Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          addGlobalMacroRule(), FileToReplacements, FileToNumberValueTrackers});
}

void AnalyzerInstrumenter::registerMatchers(clang::ast_matchers::MatchFinder &Finder) {
    for (auto &Callback : Callbacks)
        Callback.registerMatchers(Finder);
}


} // namespace analyzer