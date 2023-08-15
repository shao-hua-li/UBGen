add_library(RuleActionCallbackLib RuleActionCallback.cpp)
target_include_directories(RuleActionCallbackLib PUBLIC ${CLANG_INCLUDE_DIRS} ${LLVM_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR})

if(CLANG_LINK_CLANG_DYLIB)
    target_link_libraries(RuleActionCallbackLib PUBLIC LLVM)
    clang_target_link_libraries(RuleActionCallbackLib PUBLIC)
else()
    llvm_map_components_to_libnames(llvm_libs support core)
    target_link_libraries(RuleActionCallbackLib PUBLIC ${llvm_libs}
                                                   clangASTMatchers
                                                   clangTransformer
                                                   clangTooling)
endif(CLANG_LINK_CLANG_DYLIB)


add_library(AnalyzerInstrumenterLib AnalyzerInstrumenter.cpp)
target_include_directories(AnalyzerInstrumenterLib  PUBLIC ${CLANG_INCLUDE_DIRS} ${LLVM_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(AnalyzerInstrumenterLib PUBLIC RuleActionCallbackLib)

if(CLANG_LINK_CLANG_DYLIB)
    target_link_libraries(AnalyzerInstrumenterLib PUBLIC LLVM)
    clang_target_link_libraries(AnalyzerInstrumenterLib PUBLIC)
else()
    llvm_map_components_to_libnames(llvm_libs support core)
    target_link_libraries(AnalyzerInstrumenterLib PUBLIC ${llvm_libs}
                                                   clangASTMatchers
                                                   clangTransformer
                                                   clangTooling)
endif(CLANG_LINK_CLANG_DYLIB)

add_library(AddBracesLib AddBraces.cpp)
target_include_directories(AddBracesLib PUBLIC ${CLANG_INCLUDE_DIRS} ${LLVM_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(AddBracesLib PUBLIC RuleActionCallbackLib)

if(CLANG_LINK_CLANG_DYLIB)
    target_link_libraries(AddBracesLib PUBLIC LLVM)
    clang_target_link_libraries(AddBracesLib PUBLIC)
else()
    llvm_map_components_to_libnames(llvm_libs support core)
    target_link_libraries(AddBracesLib PUBLIC ${llvm_libs}
                                                   clangASTMatchers
                                                   clangTransformer
                                                   clangTooling)
endif(CLANG_LINK_CLANG_DYLIB)


add_library(ArrayIndexAddLib ArrayIndexAdd.cpp)
target_include_directories(ArrayIndexAddLib PUBLIC ${CLANG_INCLUDE_DIRS} ${LLVM_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(ArrayIndexAddLib PUBLIC RuleActionCallbackLib)

if(CLANG_LINK_CLANG_DYLIB)
    target_link_libraries(ArrayIndexAddLib PUBLIC LLVM)
    clang_target_link_libraries(ArrayIndexAddLib PUBLIC)
else()
    llvm_map_components_to_libnames(llvm_libs support core)
    target_link_libraries(ArrayIndexAddLib PUBLIC ${llvm_libs}
                                                   clangASTMatchers
                                                   clangTransformer
                                                   clangTooling)
endif(CLANG_LINK_CLANG_DYLIB)

add_library(StackToHeapLib StackToHeap.cpp)
target_include_directories(StackToHeapLib PUBLIC ${CLANG_INCLUDE_DIRS} ${LLVM_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(StackToHeapLib PUBLIC RuleActionCallbackLib)

if(CLANG_LINK_CLANG_DYLIB)
    target_link_libraries(StackToHeapLib PUBLIC LLVM)
    clang_target_link_libraries(StackToHeapLib PUBLIC)
else()
    llvm_map_components_to_libnames(llvm_libs support core)
    target_link_libraries(StackToHeapLib PUBLIC ${llvm_libs}
                                                   clangASTMatchers
                                                   clangTransformer
                                                   clangTooling)
endif(CLANG_LINK_CLANG_DYLIB)

add_library(IntegerAddLib IntegerAdd.cpp)
target_include_directories(IntegerAddLib PUBLIC ${CLANG_INCLUDE_DIRS} ${LLVM_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(IntegerAddLib PUBLIC RuleActionCallbackLib)

if(CLANG_LINK_CLANG_DYLIB)
    target_link_libraries(IntegerAddLib PUBLIC LLVM)
    clang_target_link_libraries(IntegerAddLib PUBLIC)
else()
    llvm_map_components_to_libnames(llvm_libs support core)
    target_link_libraries(IntegerAddLib PUBLIC ${llvm_libs}
                                                   clangASTMatchers
                                                   clangTransformer
                                                   clangTooling)
endif(CLANG_LINK_CLANG_DYLIB)

add_subdirectory(tool)
