#include "AddBraces.hpp"

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

// add braces around if/while/for/switch nodes
auto curlyBraceAction = {insertBefore(statement("stmt"), cat("{\n")),
                         insertAfter(statement("stmt"), cat("\n}"))};

/* Matchers and Rules */

AST_MATCHER_P(CaseStmt, isCaseSubStmt, ast_matchers::internal::Matcher<Stmt>,
              InnerMatcher) {
    const auto *SubStmt = Node.getSubStmt();
    return (SubStmt != nullptr &&
            InnerMatcher.matches(*SubStmt, Finder, Builder));
}

AST_MATCHER_P(DefaultStmt, isDefaultSubStmt,
              ast_matchers::internal::Matcher<Stmt>, InnerMatcher) {
    const auto *SubStmt = Node.getSubStmt();
    return (SubStmt != nullptr &&
            InnerMatcher.matches(*SubStmt, Finder, Builder));
}

// rule for if/then statements without braces
auto canonicalizeIfThenRule() {
    return makeRule(ifStmt(isExpansionInMainFile(),
                           hasThen(stmt(unless(compoundStmt())).bind("stmt"))),
                    curlyBraceAction);
}
// rule for if/else statements without braces
auto canonicalizeIfElseRule() {
    return makeRule(ifStmt(isExpansionInMainFile(),
                           hasElse(stmt(unless(compoundStmt())).bind("stmt"))),
                    curlyBraceAction);
}
// rule for loop statements without braces
auto canonicalizeLoopRule() {
    return makeRule(
        mapAnyOf(forStmt, whileStmt, doStmt, cxxForRangeStmt)
            .with(isExpansionInMainFile(),
                  hasBody(stmt(unless(compoundStmt())).bind("stmt"))),
            curlyBraceAction);
}
// rule for switch statements without braces
auto canonicalizeSwitchRule() {
    auto Unless = unless(anyOf(compoundStmt(), caseStmt(), defaultStmt()));
    return applyFirst(
        {makeRule(caseStmt(isExpansionInMainFile(),
                           isCaseSubStmt(stmt(Unless).bind("stmt"))),
                  curlyBraceAction),
         makeRule(defaultStmt(isExpansionInMainFile(),
                              isDefaultSubStmt(stmt(Unless).bind("stmt"))),
                  curlyBraceAction)});
}

} // namespace

AddBraces::AddBraces(
    std::map<std::string, clang::tooling::Replacements> &FileToReplacements)
    :  FileToReplacements{FileToReplacements} {


    // canonicalize rules
    Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          canonicalizeIfThenRule(), FileToReplacements, FileToNumberValueTrackers});
    Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          canonicalizeIfElseRule(), FileToReplacements, FileToNumberValueTrackers});
    Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          canonicalizeLoopRule(), FileToReplacements, FileToNumberValueTrackers});
    Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          canonicalizeSwitchRule(), FileToReplacements, FileToNumberValueTrackers});
}

void AddBraces::registerMatchers(clang::ast_matchers::MatchFinder &Finder) {
    for (auto &Callback : Callbacks)
        Callback.registerMatchers(Finder);
}


} // namespace analyzer