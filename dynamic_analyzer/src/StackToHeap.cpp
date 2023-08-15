#include "StackToHeap.hpp"

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
#include <random>
#include <ctime>

using namespace clang;
using namespace ast_matchers;
using namespace transformer;

namespace analyzer {

std::string heap_malloc_macro_0 = "#include<stdlib.h>";
std::string heap_malloc_macro_1 = "#define init_arr_1(arr1, arr2, arr_type) \
  arr_type * arr1 = (arr_type*)malloc(sizeof(arr_type)*(sizeof(arr2) / sizeof(arr2[0])));\
  for(int i=0; i<(sizeof(arr2) / sizeof(arr2[0])); i++){ \
    arr1[i] = arr2[i]; \
  } ";
std::string heap_malloc_macro_2 = "#define init_arr_2(arr1, arr2, arr_type) \
  arr_type** arr1 = (arr_type**)malloc(sizeof(arr_type*)*(sizeof(arr2) / sizeof(arr2[0])));\
  for(int i=0; i<(sizeof(arr2) / sizeof(arr2[0])); i++){ \
    arr1[i] = (arr_type*)malloc(sizeof(arr_type)*(sizeof(arr2[0]) / sizeof(arr2[0][0]))); \
    for(int j=0; j<(sizeof(arr2[0]) / sizeof(arr2[0][0])); j++) \
      arr1[i][j] = arr2[i][j]; \
  } ";
std::string heap_malloc_macro_3 = "#define init_arr_3(arr1, arr2, arr_type) \
  arr_type*** arr1 = (arr_type***)malloc(sizeof(arr_type**)*(sizeof(arr2) / sizeof(arr2[0])));\
  for(int i=0; i<(sizeof(arr2) / sizeof(arr2[0])); i++){ \
    arr1[i] = (arr_type**)malloc(sizeof(arr_type*)*(sizeof(arr2[0]) / sizeof(arr2[0][0]))); \
    for(int j=0; j<(sizeof(arr2[0]) / sizeof(arr2[0][0])); j++){ \
      arr1[i][j] = (arr_type*)malloc(sizeof(arr_type)*(sizeof(arr2[0][0]) / sizeof(arr2[0][0][0]))); \
      for(int k=0; k<(sizeof(arr2[0][0]) / sizeof(arr2[0][0][0])); k++) \
        arr1[i][j][k] = arr2[i][j][k]; \
    } \
  } ";

std::string heap_malloc_macro_1_uninit = "#define init_arr_1_uninit(arr1, arr2, arr_type) \
  arr_type * arr1 = (arr_type*)malloc(sizeof(arr_type)*(sizeof(arr2) / sizeof(arr2[0])));\
  ";
std::string heap_malloc_macro_2_uninit = "#define init_arr_2_uninit(arr1, arr2, arr_type) \
  arr_type** arr1 = (arr_type**)malloc(sizeof(arr_type*)*(sizeof(arr2) / sizeof(arr2[0])));\
  for(int i=0; i<(sizeof(arr2) / sizeof(arr2[0])); i++){ \
    arr1[i] = (arr_type*)malloc(sizeof(arr_type)*(sizeof(arr2[0]) / sizeof(arr2[0][0]))); \
  } ";
std::string heap_malloc_macro_3_uninit = "#define init_arr_3_uninit(arr1, arr2, arr_type) \
  arr_type*** arr1 = (arr_type***)malloc(sizeof(arr_type**)*(sizeof(arr2) / sizeof(arr2[0])));\
  for(int i=0; i<(sizeof(arr2) / sizeof(arr2[0])); i++){ \
    arr1[i] = (arr_type**)malloc(sizeof(arr_type*)*(sizeof(arr2[0]) / sizeof(arr2[0][0]))); \
    for(int j=0; j<(sizeof(arr2[0]) / sizeof(arr2[0][0])); j++){ \
      arr1[i][j] = (arr_type*)malloc(sizeof(arr_type)*(sizeof(arr2[0][0]) / sizeof(arr2[0][0][0]))); \
    } \
  } ";

std::string heap_free_macro_1 = "#define free_1(arr) \
  free(arr);";
std::string heap_free_macro_2 = "#define free_2(arr) \
  for(int i=0; i<(sizeof(arr) / sizeof(arr[0])); i++){ \
    free(arr[i]); \
  } \
  free(arr);";
std::string heap_free_macro_3 = "#define free_3(arr) \
  for(int i=0; i<(sizeof(arr) / sizeof(arr[0])); i++){ \
    for(int j=0; j<(sizeof(arr[0]) / sizeof(arr[0][0])); j++){ \
      free(arr[i][j]); \
    } \
    free(arr[i]); \
  } \
  free(arr);";


namespace {

/*
Stack variable to heap variable
*/
std::mt19937 rng(time(NULL));
std::uniform_int_distribution<int> ud(0, 100);
static int mut_prob;

class StackToHeapMut : public MatchComputation<std::string> {
  public:
    StackToHeapMut() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const ValueDecl *VD = mResult.Nodes.getNodeAs<clang::ValueDecl>("var");
        const VarDecl *var_decl = mResult.Nodes.getNodeAs<clang::VarDecl>("var");
        const ArrayType *AT = mResult.Nodes.getNodeAs<clang::ArrayType>("type");
        std::string typeStr = AT->getElementType().getAsString();
        size_t n = std::count(typeStr.begin(), typeStr.end(), '[');

        if (ud(rng) > mut_prob || typeStr.find("struct") != -1 || typeStr.find("union") != -1 || typeStr.find("const") != -1) {
            Result->append("\n");
            Result->append("#define " + VD->getNameAsString() + " MUT_" + VD->getNameAsString());
            return llvm::Error::success();
        }
        Result->append("\n/*I:ID" + std::to_string(instr_id) + ":VARDECLHEAP:" + typeStr + ":");
        Result->append(VD->getNameAsString());
        Result->append(":"+std::to_string(n+1));//log the dim of the array
        Result->append(":*/\n");
        if (var_decl->hasInit()) {
          if (n == 0) { // 1-dim array
              Result->append("init_arr_1");
          } else if (n == 1) {
              Result->append("init_arr_2");
          } else if (n == 2) {
              Result->append("init_arr_3");
          }
        } else {
          if (n == 0) { // 1-dim array
              Result->append("init_arr_1_uninit");
          } else if (n == 1) {
              Result->append("init_arr_2_uninit");
          } else if (n == 2) {
              Result->append("init_arr_3_uninit");
          }
        }
        
        typeStr = std::regex_replace(typeStr, std::regex("const"), "");
        typeStr = std::regex_replace(typeStr, std::regex("\[[\\d|+|\\-]+\]"), "");

        Result->append("("+VD->getNameAsString() + ", MUT_" + VD->getNameAsString() + ", " + typeStr + ")");
        instr_id++;
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
    static int instr_id;
};

int StackToHeapMut::instr_id = 0;

auto stackToHeapAction = {
    insertBefore(name("arr"), cat("MUT_")),
    insertAfter(statement("arr"), cat(std::make_unique<StackToHeapMut>())),
};


class FreeHeapMut : public MatchComputation<std::string> {
  public:
    FreeHeapMut() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &mResult,
                     std::string *Result) const override {
        const ValueDecl *VD = mResult.Nodes.getNodeAs<clang::ValueDecl>("var");
        const VarDecl *var_decl = mResult.Nodes.getNodeAs<clang::VarDecl>("var");
        const ArrayType *AT = mResult.Nodes.getNodeAs<clang::ArrayType>("type");
        const ReturnStmt *RET = mResult.Nodes.getNodeAs<clang::ReturnStmt>("return");
        std::string ret_expr = getExprAsText(RET->getRetValue(), *mResult.SourceManager, mResult.Context->getLangOpts());
        if (ret_expr.find(VD->getNameAsString()) != -1) {
          return llvm::Error::success();
        }
        std::string typeStr = AT->getElementType().getAsString();
        size_t n = std::count(typeStr.begin(), typeStr.end(), '[');
        if (typeStr.find("struct") != -1 || typeStr.find("union") != -1 || typeStr.find("const") != -1) {
            return llvm::Error::success();
        }
        Result->append("/*I:ID");
        Result->append(std::to_string(instr_id));
        Result->append(":VARREF_FREE:");
        Result->append(typeStr + ":");
        Result->append(VD->getNameAsString());
        Result->append(":*/\n");
        instr_id++;
        if (n == 0) { // 1-dim array
            Result->append("free_1");
        } else if (n == 1) {
            Result->append("free_2");
        } else if (n == 2) {
            Result->append("free_3");
        }
        
        Result->append("("+VD->getNameAsString() +");\n");
        return llvm::Error::success();
    }
    std::string toString() const override { return "{}"; }
    static int instr_id;
    static std::string getExprAsText(const Expr *E, const SourceManager &SM, const LangOptions &lp) {
        auto SR = CharSourceRange::getTokenRange(E->getSourceRange());
        return Lexer::getSourceText(SR, SM, lp).str();
    }
};
int FreeHeapMut::instr_id = 0;

auto freeHeapAction = {
    insertBefore(statement("return"), cat(std::make_unique<FreeHeapMut>()))
};



auto stackToHeapRule() {
    return makeRule(varDecl(
        anyOf(hasLocalStorage(), isStaticLocal()),
        unless(hasType(isConstQualified())),
        isExpansionInMainFile(),
        unless(hasAncestor(functionDecl(isMain()))),
        hasType(arrayType().bind("type")),
        valueDecl().bind("var")
        ).bind("arr"),
        stackToHeapAction);
}

auto freeHeapRule() {
  return makeRule(varDecl(
        anyOf(hasLocalStorage(), isStaticLocal()),
        unless(hasType(isConstQualified())),
        isExpansionInMainFile(),
        unless(hasAncestor(functionDecl(isMain()))),
        hasType(arrayType().bind("type")),
        valueDecl().bind("var"),
        hasParent(declStmt(hasParent(compoundStmt(forEachDescendant(returnStmt().bind("return"))))))
        ).bind("arr"),
        freeHeapAction);
}


/*
Generate Heap malloc macros
*/
class HeapMallocGenerator : public MatchComputation<std::string> {
  public:
    HeapMallocGenerator() = default;
    llvm::Error eval(const ast_matchers::MatchFinder::MatchResult &,
                     std::string *Result) const override {
        Result->append(heap_malloc_macro_0);
        Result->append("\n");
        Result->append(heap_malloc_macro_1);
        Result->append("\n");
        Result->append(heap_malloc_macro_2);
        Result->append("\n");
        Result->append(heap_malloc_macro_3);
        Result->append("\n");
        Result->append(heap_malloc_macro_1_uninit);
        Result->append("\n");
        Result->append(heap_malloc_macro_2_uninit);
        Result->append("\n");
        Result->append(heap_malloc_macro_3_uninit);
        Result->append("\n");
        Result->append(heap_free_macro_1);
        Result->append("\n");
        Result->append(heap_free_macro_2);
        Result->append("\n");
        Result->append(heap_free_macro_3);
        Result->append("\n");
        Result->append("/*I::*/ int print_flag_free[" + std::to_string(FreeHeapMut::instr_id) + "];\n");
        return llvm::Error::success();
    }

    std::string toString() const override {
        return "HeapMallocGenerator;\n";
    }
};

auto addHeapMallocMacroRule() {
    return makeRule(functionDecl(
        isExpansionInMainFile(),
        isMain()
        ).bind("main"),
        insertAfter(ruleactioncallback::startOfFile("main"), std::make_unique<HeapMallocGenerator>()));
}


auto allRules() {
    return applyFirst({
        stackToHeapRule(),
        addHeapMallocMacroRule()
    });
}

} // namespace

StackToHeap::StackToHeap(
    std::map<std::string, clang::tooling::Replacements> &FileToReplacements, int MutProb)
    :  FileToReplacements{FileToReplacements} {

    mut_prob = MutProb;

    Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
          allRules(), FileToReplacements, FileToNumberValueTrackers});
    if (mut_prob == 100) {
      Callbacks.emplace_back(ruleactioncallback::RuleActionCallback{
            freeHeapRule(), FileToReplacements, FileToNumberValueTrackers});
    }
}

void StackToHeap::registerMatchers(clang::ast_matchers::MatchFinder &Finder) {
    for (auto &Callback : Callbacks)
        Callback.registerMatchers(Finder);
}


} // namespace analyzer