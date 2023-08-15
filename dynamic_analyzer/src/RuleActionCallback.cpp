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

#include "RuleActionCallback.hpp"

using namespace clang;
using namespace ast_matchers;
using namespace transformer;

namespace ruleactioncallback {
std::string GetFilenameFromRange(const CharSourceRange &R,
                                const SourceManager &SM) {
    const std::pair<FileID, unsigned> DecomposedLocation =
        SM.getDecomposedLoc(SM.getSpellingLoc(R.getBegin()));
    const FileEntry *Entry = SM.getFileEntryForID(DecomposedLocation.first);
return std::string(Entry ? Entry->getName() : "");

}

Expected<DynTypedNode> getNode(const ast_matchers::BoundNodes &Nodes,
                               StringRef ID) {
    auto &NodesMap = Nodes.getMap();
    auto It = NodesMap.find(ID);
    if (It == NodesMap.end())
        return llvm::make_error<llvm::StringError>(llvm::errc::invalid_argument,
                                                   ID + "not bound");
    return It->second;
}

RangeSelector startOfFile(std::string ID) {
    return [ID](const clang::ast_matchers::MatchFinder::MatchResult &Result)
               -> Expected<CharSourceRange> {
        auto Node = getNode(Result.Nodes, ID);
        if (!Node)
            return Node.takeError();
        const auto &SM = Result.Context->getSourceManager();
        auto Start = SM.getLocForStartOfFile(
            SM.getFileID(Node->getSourceRange().getBegin()));
        return CharSourceRange(SourceRange(Start), false);
    };
}

}//namespace: ruleactioncallback

ruleactioncallback::RuleActionCallback::RuleActionCallback(
    RewriteRule Rule,
    std::map<std::string, clang::tooling::Replacements> &FileToReplacements,
    std::map<std::string, int> &FileToNumberValueTrackers)
    : Rule{Rule}, FileToReplacements{FileToReplacements},
      FileToNumberValueTrackers{FileToNumberValueTrackers} {}

void ruleactioncallback::RuleActionCallback::run(
    const clang::ast_matchers::MatchFinder::MatchResult &Result) {

    
    if (Result.Context->getDiagnostics().hasErrorOccurred()) {
        llvm::errs() << "An error has occured.\n";
        return;
    }
    Expected<SmallVector<transformer::Edit, 1>> Edits =
        transformer::detail::findSelectedCase(Result, Rule).Edits(Result);
    if (!Edits) {
        llvm::errs() << "Rewrite failed: " << llvm::toString(Edits.takeError())
                     << "\n";
        return;
    }
    auto SM = Result.SourceManager;
    for (const auto &T : *Edits) {
        assert(T.Kind == transformer::EditKind::Range);
        auto FilePath = GetFilenameFromRange(T.Range, *SM);
        auto N = FileToNumberValueTrackers[FilePath]++;
        auto R = tooling::Replacement(
            *SM, T.Range, T.Replacement);
        auto &Replacements = FileToReplacements[FilePath];
        auto Err = Replacements.add(R);
        if (Err) {
            auto NewOffset = Replacements.getShiftedCodePosition(R.getOffset());
            auto NewLength = Replacements.getShiftedCodePosition(
                                 R.getOffset() + R.getLength()) -
                             NewOffset;
            if (NewLength == R.getLength()) {
                R = clang::tooling::Replacement(R.getFilePath(), NewOffset,
                                                NewLength,
                                                R.getReplacementText());
                Replacements = Replacements.merge(tooling::Replacements(R));
            } else {
                llvm_unreachable(llvm::toString(std::move(Err)).c_str());
            }
        }
    }

}

void ruleactioncallback::RuleActionCallback::registerMatchers(
    clang::ast_matchers::MatchFinder &Finder) {
    for (auto &Matcher : transformer::detail::buildMatchers(Rule))
        Finder.addDynamicMatcher(
            Matcher.withTraversalKind(clang::TK_IgnoreUnlessSpelledInSource),
            this);
}
