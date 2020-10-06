INCLUDE_DIRS =
LINK_DIRS = 

OUTPUT_DIR = ../bin
SOLVER_OUTPUT_FILE = solver.exe
VISUALISER_OUTPUT_FILE = visualiser.exe


CXX=g++
LIBS = 
INCLUDE_FLAGS=$(INCLUDE_DIRS:%=-I%)
LINK_FLAGS=$(LINK_DIRS:%=-L%)
LIB_FLAGS=$(LIBS:%=-l%)
CXXFLAGS = -std=c++14 $(INCLUDE_FLAGS) $(LINK_FLAGS) $(LIB_FLAGS)
RELEASE_FLAGS = -O3 
DEBUG_FLAGS = -Og -Wall 

COMMON_FILES = instance.cpp
SOLVER_FILES = simple_solver.cpp solver_main.cpp
VISUALISER_FILES = visualiser.cpp visualiser_main.cpp

release: solver visualiser

#debug: main.cpp
#	$(PROTOBUF_GENERATE)
#	$(CXX) $(CXXFLAGS) $(DEBUG_FLAGS) $(CPP_FILES) -o $(OUTPUT_FILE)

solver: common.o
	$(CXX) $(CXXFLAGS) $(RELEASE_FLAGS) $(SOLVER_FILES) common.o -o $(OUTPUT_DIR)/$(SOLVER_OUTPUT_FILE)

visualiser: common.o
	$(CXX) $(CXXFLAGS) $(RELEASE_FLAGS) $(VISUALISER_FILES) common.o -Dcimg_display=0 -o $(OUTPUT_DIR)/$(VISUALISER_OUTPUT_FILE)

common.o:
	$(CXX) $(CXXFLAGS) $(RELEASE_FLAGS) -c $(COMMON_FILES) -o common.o