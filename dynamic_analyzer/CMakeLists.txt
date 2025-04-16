cmake_minimum_required(VERSION 3.19)
project(DynamicAnalyzer LANGUAGES CXX C)

find_package(LLVM REQUIRED CONFIG)

message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in ${LLVM_DIR}")

list(APPEND CMAKE_MODULE_PATH ${LLVM_CMAKE_DIR})

find_package(Clang REQUIRED CONFIG)
message(STATUS "Using ClangConfig.cmake in ${Clang_DIR}")
list(APPEND CMAKE_MODULE_PATH ${CLANG_CMAKE_DIR})
include(${CLANG_CMAKE_DIR}/AddClang.cmake)

if("${LLVM_VERSION_MAJOR}" VERSION_LESS 18)
  message(FATAL_ERROR "Found LLVM ${LLVM_VERSION_MAJOR}, but need LLVM >= 18")
endif()

if("${Clang_VERSION_MAJOR}" VERSION_LESS 18)
  message(FATAL_ERROR "Found Clang ${Clang_VERSION}, but need Clang >= 18")
endif()

if (NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif ()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic -march=native")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -w")
set(CMAKE_CXX_STANDARD 17)

if(${LLVM_REQUIRES_RTTI})
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")
endif(${LLVM_REQUIRES_RTTI})

separate_arguments(LLVM_DEFINITIONS_LIST NATIVE_COMMAND ${LLVM_DEFINITIONS})
add_definitions(${LLVM_DEFINITIONS_LIST})

if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
   add_compile_options (-fdiagnostics-color=always)
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
   add_compile_options (-fcolor-diagnostics)
endif ()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

add_subdirectory(src)


IF (BUILD_TESTING)
    include(CTest)
    enable_testing()
    find_package(Catch2 REQUIRED)
    include(CTest)
    include(Catch)
    add_subdirectory(test)
ENDIF(BUILD_TESTING)
