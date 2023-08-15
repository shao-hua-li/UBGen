#include <clang/Frontend/TextDiagnosticPrinter.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Tooling/CommonOptionsParser.h>
#include <clang/Tooling/Refactoring.h>

#include <llvm/Support/CommandLine.h>
#include <llvm/Support/raw_ostream.h>
#include <type_traits>

#include <ArrayIndexAdd.hpp>

#include <iostream>

using namespace llvm;
using namespace clang;
using namespace clang::tooling;
using namespace clang::ast_matchers;

namespace {

cl::OptionCategory ToolOptions("options");

bool applyReplacements(RefactoringTool &Tool) {
    LangOptions DefaultLangOptions;
    IntrusiveRefCntPtr<DiagnosticOptions> DiagOpts = new DiagnosticOptions();
    clang::TextDiagnosticPrinter DiagnosticPrinter(errs(), &*DiagOpts);
    DiagnosticsEngine Diagnostics(
        IntrusiveRefCntPtr<DiagnosticIDs>(new DiagnosticIDs()), &*DiagOpts,
        &DiagnosticPrinter, false);
    auto &FileMgr = Tool.getFiles();
    SourceManager Sources(Diagnostics, FileMgr);

    Rewriter Rewrite(Sources, DefaultLangOptions);

    bool Result = true;
    for (const auto &FileAndReplaces : groupReplacementsByFile(
             Rewrite.getSourceMgr().getFileManager(), Tool.getReplacements())) {
        auto &CurReplaces = FileAndReplaces.second;

        Result = applyAllReplacements(CurReplaces, Rewrite) && Result;
    }
    if (!Result) {
        llvm::errs() << "Failed applying all replacements.\n";
        return false;
    }

    return !Rewrite.overwriteChangedFiles();
}

template <typename InstrTool> int runToolOnCode(RefactoringTool &Tool) {
    InstrTool Instr(Tool.getReplacements());
    ast_matchers::MatchFinder Finder;
    Instr.registerMatchers(Finder);
    std::unique_ptr<tooling::FrontendActionFactory> Factory =
        tooling::newFrontendActionFactory(&Finder);

    auto Ret = Tool.run(Factory.get());
    if (!Ret)
        if (!applyReplacements(Tool)) {
            llvm::errs() << "Failed to overwrite the input files.\n";
            return 1;
        }

    return Ret;
}


} // namespace

int main(int argc, const char **argv) {
    auto ExpectedParser =
        CommonOptionsParser::create(argc, argv, ToolOptions);
    if (!ExpectedParser) {
        llvm::errs() << ExpectedParser.takeError();
        return 1;
    }
    CommonOptionsParser &OptionsParser = ExpectedParser.get();

    const auto &Compilations = OptionsParser.getCompilations();
    const auto &Files = OptionsParser.getSourcePathList();
    RefactoringTool Tool(Compilations, Files);
    int Result = 0;
    Result = runToolOnCode<analyzer::ArrayIndexAdd>(Tool);

    if (Result) {
        llvm::errs() << "Something went wrong...\n";
        return Result;
    }

    return 0;
}