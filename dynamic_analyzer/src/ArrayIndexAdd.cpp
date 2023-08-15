#include "ArrayIndexAdd.hpp"

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

/* 
    ArrayIndexMut
*/
class ArrayIndexMut : public MatchComputation<std::string> {
  public:
    ArrayIndexMut() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &,
                     std::string *Result) const override {
        Result->append(") _MUTARR" + std::to_string(num_mutate) + ")");
        num_mutate++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }

    static int num_mutate;
};
int ArrayIndexMut::num_mutate = 0;

auto addArrayIndexRule () {
    auto arrayMatcher = arraySubscriptExpr(
        isExpansionInMainFile(), 
        unless(hasAncestor(arraySubscriptExpr())), 
        unless(hasAncestor(functionDecl(isMain()))), 
        unless(hasAncestor(varDecl())),
        hasBase(hasDescendant(declRefExpr(hasDeclaration(varDecl().bind("var"))))), 
        hasIndex(expr().bind("idx"))
    );
    return makeRule(arrayMatcher, {
        insertBefore(node("idx"), cat("((")), 
        insertAfter(statement("idx"), std::make_unique<ArrayIndexMut>())
    });
}

/* 
    PointerIndexMut
*/
class PointerIndexMut : public MatchComputation<std::string> {
  public:
    PointerIndexMut() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &,
                     std::string *Result) const override {
        Result->append(") _MUTPTR" + std::to_string(num_mutate) + ")");
        num_mutate++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }

    static int num_mutate;
};
int PointerIndexMut::num_mutate = 0;

auto addPointerIndexRule () {
    auto pointerMatcher = unaryOperator(
            isExpansionInMainFile(),
            unless(hasAncestor(functionDecl(isMain()))),
            unless(hasAncestor(varDecl())), 
            hasAnyOperatorName("*"),
            unless(hasAncestor(unaryOperator(hasOperatorName("++")))), 
            unless(hasAncestor(unaryOperator(hasOperatorName("--")))),
            has(expr().bind("ptr")),
            hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
            );
    auto memberExprMatcher = memberExpr(
            isExpansionInMainFile(),
            unless(hasAncestor(functionDecl(isMain()))),
            unless(hasAncestor(varDecl())), 
            hasDescendant(expr().bind("ptr")),
            hasAncestor(stmt(hasParent(compoundStmt())).bind("stmt"))
            );
    auto mutatePointerAction = {
        insertBefore(node("ptr"), cat("((")),
        insertAfter(node("ptr"), std::make_unique<PointerIndexMut>())
    };
    return applyFirst({
        makeRule(pointerMatcher, mutatePointerAction),
        makeRule(memberExprMatcher, mutatePointerAction)
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
        for (int i=0; i < ArrayIndexMut::num_mutate; i++) {
          Result->append("#define _MUTARR" + std::to_string(i) + " \n");
        }
        for (int i=0; i < PointerIndexMut::num_mutate; i++) {
          Result->append("#define _MUTPTR" + std::to_string(i) + " \n");
        }
        return llvm::Error::success();
    }

    std::string toString() const override {
        return "DynamicAnalyzerError\n";
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
        addArrayIndexRule(),
        addPointerIndexRule(),
        addGlobalMacroRule()
    });
}

} // namespace

ArrayIndexAdd::ArrayIndexAdd(
    std::map<std::string, clang::tooling::Replacements> &FileToReplacements)
    :  FileToReplacements{FileToReplacements} {

    Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          allRules(), FileToReplacements, FileToNumberValueTrackers});
}

void ArrayIndexAdd::registerMatchers(clang::ast_matchers::MatchFinder &Finder) {
    for (auto &Callback : Callbacks)
        Callback.registerMatchers(Finder);
}


} // namespace analyzer