#pragma once

#include <clang/ASTMatchers/ASTMatchFinder.h>
#include <clang/Tooling/Core/Replacement.h>
#include <clang/Tooling/Transformer/RewriteRule.h>

#include "RuleActionCallback.hpp"

namespace analyzer {

class AddBraces {
  public:
    AddBraces(std::map<std::string, clang::tooling::Replacements>
                    &FileToReplacements);
    AddBraces(const AddBraces &) = delete;
    AddBraces(AddBraces &&) = delete;

    void registerMatchers(clang::ast_matchers::MatchFinder &Finder);


  private:
    std::map<std::string, clang::tooling::Replacements> &FileToReplacements;
    std::vector<ruleactioncallback::RuleActionCallback> Callbacks;
    std::map<std::string, int> FileToNumberValueTrackers;
};
} // namespace analyzer