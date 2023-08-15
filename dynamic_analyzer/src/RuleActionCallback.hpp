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

namespace ruleactioncallback {

class RuleActionCallback
    : public clang::ast_matchers::MatchFinder::MatchCallback {
  public:
    RuleActionCallback(
        clang::transformer::RewriteRule Rule,
        std::map<std::string, clang::tooling::Replacements> &FileToReplacements,
        std::map<std::string, int> &FileToNumberValueTrackers);
    void
    run(const clang::ast_matchers::MatchFinder::MatchResult &Result) override;
    void registerMatchers(clang::ast_matchers::MatchFinder &Finder);
    std::string getFunctionAsText(const clang::Decl *F,
                                  const clang::SourceManager &SM, const clang::LangOptions &lp);
    
  private:
    clang::transformer::RewriteRule Rule;
    std::map<std::string, clang::tooling::Replacements> &FileToReplacements;
    std::map<std::string, int> &FileToNumberValueTrackers;
};

std::string GetFilenameFromRange(const CharSourceRange &R, const SourceManager &SM);
RangeSelector startOfFile(std::string ID);

}
