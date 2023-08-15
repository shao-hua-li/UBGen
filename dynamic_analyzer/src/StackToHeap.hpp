#pragma once

#include <clang/ASTMatchers/ASTMatchFinder.h>
#include <clang/Tooling/Core/Replacement.h>
#include <clang/Tooling/Transformer/RewriteRule.h>

#include "RuleActionCallback.hpp"

namespace analyzer {

class StackToHeap {
  public:
    StackToHeap(std::map<std::string, clang::tooling::Replacements> &FileToReplacements, int MutProb);
    StackToHeap(const StackToHeap &) = delete;
    StackToHeap(StackToHeap &&) = delete;

    void registerMatchers(clang::ast_matchers::MatchFinder &Finder);


  private:
    std::map<std::string, clang::tooling::Replacements> &FileToReplacements;
    std::vector<ruleactioncallback::RuleActionCallback> Callbacks;
    std::map<std::string, int> FileToNumberValueTrackers;
};
} // namespace analyzer