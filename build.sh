#!/bin/bash -e

# This script is to build the dynamic_analyzer used by ubsmith

# building dynamic_analyzer
cd dynamic_analyzer
rm -rf build/
mkdir build/
cd build/
cmake ..
make
