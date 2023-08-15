#include "IntegerAdd.hpp"

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
    IntegerMut
*/
class IntegerMutLeft : public MatchComputation<std::string> {
  public:
    IntegerMutLeft() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const Expr *lhs = mResult.Nodes.getNodeAs<clang::Expr>("lhs");
        Result->append(") _INTOPL" + std::to_string(instr_id) + ")");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }

    static int instr_id;
};
int IntegerMutLeft::instr_id = 0;

class IntegerMutRight : public MatchComputation<std::string> {
  public:
    IntegerMutRight() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const Expr *rhs = mResult.Nodes.getNodeAs<clang::Expr>("rhs");
        Result->append(") _INTOPR" + std::to_string(instr_id) + ")");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }

    static int instr_id;
};
int IntegerMutRight::instr_id = 0;

auto addIntegerMutRule () {
    auto operandMather = 
            binaryOperator(
                isExpansionInMainFile(),
                hasAnyOperatorName("+", "-", "*", "/", "<<", ">>", "%"),
                unless(hasParent(forStmt())), // avoid matching for increment statement
                hasLHS(expr().bind("lhs")),
                hasRHS(expr().bind("rhs"))
            );
    auto actions = {
        insertBefore(node("lhs"), cat("((")),
        insertAfter(node("lhs"), std::make_unique<IntegerMutLeft>()),
        insertBefore(node("rhs"), cat("((")),
        insertAfter(node("rhs"), std::make_unique<IntegerMutRight>())
    };
    return makeRule(operandMather, actions);
}

/* 
    AddGlobalMacro
*/
class AddGlobalMacro : public MatchComputation<std::string> {
  public:
    AddGlobalMacro() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &,
                     std::string *Result) const override {
        for (int i=0; i < IntegerMutLeft::instr_id; i++) {
          Result->append("#define _INTOPL" + std::to_string(i) + " \n");
        }
        for (int i=0; i < IntegerMutRight::instr_id; i++) {
          Result->append("#define _INTOPR" + std::to_string(i) + " \n");
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
        addIntegerMutRule(),
        addGlobalMacroRule()
    });
}

} // namespace

IntegerAdd::IntegerAdd(
    std::map<std::string, clang::tooling::Replacements> &FileToReplacements)
    :  FileToReplacements{FileToReplacements} {

    Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          allRules(), FileToReplacements, FileToNumberValueTrackers});
}

void IntegerAdd::registerMatchers(clang::ast_matchers::MatchFinder &Finder) {
    for (auto &Callback : Callbacks)
        Callback.registerMatchers(Finder);
}


} // namespace analyzer