add_executable(tool-addbraces ToolAddBraces.cpp)
target_link_libraries(tool-addbraces PUBLIC AddBracesLib)
install(TARGETS tool-addbraces DESTINATION bin)

add_executable(tool-instrumenter ToolInstrumenter.cpp)
target_link_libraries(tool-instrumenter PUBLIC AnalyzerInstrumenterLib)
install(TARGETS tool-instrumenter DESTINATION bin)

add_executable(tool-addarrayindex ToolAddArrayIndex.cpp)
target_link_libraries(tool-addarrayindex PUBLIC ArrayIndexAddLib)
install(TARGETS tool-addarrayindex DESTINATION bin)

add_executable(tool-stacktoheap ToolStackToHeap.cpp)
target_link_libraries(tool-stacktoheap PUBLIC StackToHeapLib)
install(TARGETS tool-stacktoheap DESTINATION bin)

add_executable(tool-addinteger ToolAddInteger.cpp)
target_link_libraries(tool-addinteger PUBLIC IntegerAddLib)
install(TARGETS tool-addinteger DESTINATION bin)

