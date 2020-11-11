GUROBI_HOME = /opt/gurobi900/linux64
GUROBI_PARAMS = -I$(GUROBI_HOME)/include -L$(GUROBI_HOME)/lib -lgurobi90
GUROBI_INPUT = ~/gurobi/build/*o

INCLUDE_DIRS = lib
LINK_DIRS = 

OUTPUT_DIR = ../bin
COMMON_DIR = common
GENERATOR_DIR = generator
VISUALISER_DIR = visualiser
SOLVER_DIR = solver
STAT_DIR = stat
ILP_SOLVER_DIR = ilp_solver
ILP_RES_ASSIGNER_DIR = ilp_res_assigner
GENERATOR_OUTPUT_FILE = generator.exe
SOLVER_OUTPUT_FILE = solver.exe
VISUALISER_OUTPUT_FILE = visualiser.exe
STAT_OUTPUT_FILE = stat.exe
ILP_SOLVER_OUTPUT_FILE = ilp_solver.exe
ILP_RES_ASSIGNER_OUTPUT_FILE = ilp_res_assigner.exe


CXX=g++
LIBS = 
INCLUDE_FLAGS=$(INCLUDE_DIRS:%=-I%)
LINK_FLAGS=$(LINK_DIRS:%=-L%)
LIB_FLAGS=$(LIBS:%=-l%)
CXXFLAGS = -std=c++14 $(INCLUDE_FLAGS) $(LINK_FLAGS) $(LIB_FLAGS)
RELEASE_FLAGS = -O3 
DEBUG_FLAGS = -Og -g -Wall 

COMMON_FILES = $(COMMON_DIR)/instance.cpp $(COMMON_DIR)/arg_parser.cpp
GENERATOR_FILES = $(GENERATOR_DIR)/main.cpp $(GENERATOR_DIR)/generator.cpp
SOLVER_FILES = $(SOLVER_DIR)/main.cpp $(SOLVER_DIR)/solver.cpp  $(SOLVER_DIR)/longest_tasks_first_solver.cpp $(SOLVER_DIR)/random_task_order_solver.cpp 
VISUALISER_FILES = $(VISUALISER_DIR)/main.cpp $(VISUALISER_DIR)/visualiser.cpp 
STAT_FILES = $(STAT_DIR)/main.cpp
ILP_SOLVER_FILES = $(ILP_SOLVER_DIR)/main.cpp
ILP_RES_ASSIGNER_FILES = $(ILP_RES_ASSIGNER_DIR)/main.cpp


.PHONY: generator solver visualiser visualiser-display stat ilp-solver ilp-res-assigner
release: generator solver visualiser stat

generator: 
	$(CXX) $(CXXFLAGS) $(RELEASE_FLAGS) $(COMMON_FILES) $(GENERATOR_FILES) -o $(OUTPUT_DIR)/$(GENERATOR_OUTPUT_FILE)

solver: 
	$(CXX) $(CXXFLAGS) $(RELEASE_FLAGS) $(COMMON_FILES) $(SOLVER_FILES) -o $(OUTPUT_DIR)/$(SOLVER_OUTPUT_FILE)

visualiser: 
	$(CXX) $(CXXFLAGS) $(RELEASE_FLAGS) $(COMMON_FILES) $(VISUALISER_FILES) lib/lodepng.cpp -Dcimg_display=0 -U__STRICT_ANSI__ -o $(OUTPUT_DIR)/$(VISUALISER_OUTPUT_FILE)

visualiser-display: 
	$(CXX) $(CXXFLAGS) -lgdi32 $(RELEASE_FLAGS) $(COMMON_FILES) $(VISUALISER_FILES) lib/lodepng.cpp -U__STRICT_ANSI__ -o $(OUTPUT_DIR)/$(VISUALISER_OUTPUT_FILE)

stat: 
	$(CXX) $(CXXFLAGS) $(RELEASE_FLAGS) $(COMMON_FILES) $(STAT_FILES) -o $(OUTPUT_DIR)/$(STAT_OUTPUT_FILE)

ilp: ilp-solver ilp-res-assigner

ilp-solver:
	$(CXX) $(CXXFLAGS) $(RELEASE_FLAGS) $(GUROBI_PARAMS) $(COMMON_FILES) $(ILP_SOLVER_FILES) $(GUROBI_INPUT) -o $(OUTPUT_DIR)/$(ILP_SOLVER_OUTPUT_FILE)

ilp-res-assigner:
	$(CXX) $(CXXFLAGS) $(RELEASE_FLAGS) $(GUROBI_PARAMS) $(COMMON_FILES) $(ILP_RES_ASSIGNER_FILES) $(GUROBI_INPUT) -o $(OUTPUT_DIR)/$(ILP_RES_ASSIGNER_OUTPUT_FILE)