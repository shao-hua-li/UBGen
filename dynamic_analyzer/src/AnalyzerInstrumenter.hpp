#pragma once

#include <clang/ASTMatchers/ASTMatchFinder.h>
#include <clang/Tooling/Core/Replacement.h>
#include <clang/Tooling/Transformer/RewriteRule.h>

#include "RuleActionCallback.hpp"

namespace analyzer {
  
enum class ToolMode {ArrayPointerIndex, ArrayIndex, PointerIndex, Memory, Pointer, Integer, Divider, Init};

class AnalyzerInstrumenter {
  public:
    AnalyzerInstrumenter(std::map<std::string, clang::tooling::Replacements>
                    &FileToReplacements, ToolMode mode);
    AnalyzerInstrumenter(const AnalyzerInstrumenter &) = delete;
    AnalyzerInstrumenter(AnalyzerInstrumenter &&) = delete;

    void registerMatchers(clang::ast_matchers::MatchFinder &Finder);


  private:
    std::map<std::string, clang::tooling::Replacements> &FileToReplacements;
    std::vector<ruleactioncallback::RuleActionCallback> Callbacks;
    std::map<std::string, int> FileToNumberValueTrackers;
};
} // namespace analyzer