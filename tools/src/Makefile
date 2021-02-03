GUROBI_HOME = /opt/gurobi910/linux64
GUROBI_PARAMS = -I$(GUROBI_HOME)/include -L$(GUROBI_HOME)/lib -lgurobi_g++5.2 -lgurobi91

INCLUDE_DIRS = lib
LINK_DIRS = 

OUTPUT_DIR = ../bin
GENERATOR_OUTPUT_FILE = generator.exe
P1_GENERATOR_OUTPUT_FILE = p1_generator.exe
SOLVER_OUTPUT_FILE = solver.exe
GLOBAL_SOLVER_OUTPUT_FILE = global_solver.exe
VISUALISER_OUTPUT_FILE = visualiser.exe
STAT_OUTPUT_FILE = stat.exe
DEMOS_CONFIG_EXPORT_OUTPUT_FILE = demos_config_export.exe
ILP_SOLVER_OUTPUT_FILE = ilp_solver.exe
ILP_RES_ASSIGNER_OUTPUT_FILE = ilp_res_assigner.exe
ILP_GLOBAL_SOLVER_OUTPUT_FILE = ilp_global_solver.exe

COMMON_DIR = common
GENERATOR_DIR = generator
P1_GENERATOR_DIR = p1_generator
VISUALISER_DIR = visualiser
SOLVER_DIR = solver
GLOBAL_SOLVER_DIR = global_solver
STAT_DIR = stat
DEMOS_CONFIG_EXPORT_DIR = demos_config_export
ILP_SOLVER_DIR = ilp_solver
ILP_RES_ASSIGNER_DIR = ilp_res_assigner
ILP_GLOBAL_SOLVER_DIR = ilp_global_solver

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
P1_GENERATOR_FILES = $(P1_GENERATOR_DIR)/main.cpp $(P1_GENERATOR_DIR)/p1_generator.cpp
SOLVER_FILES = $(SOLVER_DIR)/main.cpp $(SOLVER_DIR)/solver.cpp  $(SOLVER_DIR)/longest_tasks_first_solver.cpp $(SOLVER_DIR)/random_task_order_solver.cpp 
GLOBAL_SOLVER_FILES = $(GLOBAL_SOLVER_DIR)/main.cpp $(GLOBAL_SOLVER_DIR)/global_solver.cpp $(GLOBAL_SOLVER_DIR)/random_global_solver.cpp
VISUALISER_FILES = $(VISUALISER_DIR)/main.cpp $(VISUALISER_DIR)/visualiser.cpp 
STAT_FILES = $(STAT_DIR)/main.cpp
DEMOS_CONFIG_EXPORT_FILES = $(DEMOS_CONFIG_EXPORT_DIR)/main.cpp $(DEMOS_CONFIG_EXPORT_DIR)/demos_config_writer.cpp
ILP_COMMON_FILES = $(COMMON_DIR)/ilp_util.cpp
ILP_SOLVER_FILES = $(ILP_COMMON_FILES) $(ILP_SOLVER_DIR)/main.cpp 
ILP_RES_ASSIGNER_FILES = $(ILP_COMMON_FILES) $(ILP_RES_ASSIGNER_DIR)/main.cpp
ILP_GLOBAL_SOLVER_FILES = $(ILP_COMMON_FILES) $(ILP_GLOBAL_SOLVER_DIR)/main.cpp


.PHONY: generator p1-generator solver global-solver visualiser visualiser-display stat demos-config-export ilp-solver ilp-res-assigner ilp-global-solver
tools: generator p1-generator solver global-solver visualiser stat demos-config-export
all: tools ilp
tools-vd: generator p1-generator solver visualiser-display stat demos-config-export

generator: 
	$(CXX) $(COMMON_FILES) $(GENERATOR_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(GENERATOR_OUTPUT_FILE)

p1-generator:
	$(CXX) $(COMMON_FILES) $(P1_GENERATOR_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(P1_GENERATOR_OUTPUT_FILE)	

solver: 
	$(CXX) $(COMMON_FILES) $(SOLVER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(SOLVER_OUTPUT_FILE)

global-solver:
	$(CXX) $(COMMON_FILES) $(GLOBAL_SOLVER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(GLOBAL_SOLVER_OUTPUT_FILE)

visualiser: 
	$(CXX) $(COMMON_FILES) $(VISUALISER_FILES) lib/lodepng.cpp -Dcimg_display=0 -U__STRICT_ANSI__ $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(VISUALISER_OUTPUT_FILE)

visualiser-display: 
	$(CXX) $(COMMON_FILES) $(VISUALISER_FILES) lib/lodepng.cpp -U__STRICT_ANSI__ $(CXXFLAGS) -lgdi32 $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(VISUALISER_OUTPUT_FILE)

stat: 
	$(CXX) $(COMMON_FILES) $(STAT_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(STAT_OUTPUT_FILE)

demos-config-export:
	$(CXX) $(COMMON_FILES) $(DEMOS_CONFIG_EXPORT_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(DEMOS_CONFIG_EXPORT_OUTPUT_FILE)

ilp: ilp-solver ilp-res-assigner ilp-global-solver

ilp-solver:
	$(CXX) $(COMMON_FILES) $(ILP_SOLVER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) $(GUROBI_PARAMS) -o $(OUTPUT_DIR)/$(ILP_SOLVER_OUTPUT_FILE)

ilp-res-assigner:
	$(CXX) $(COMMON_FILES) $(ILP_RES_ASSIGNER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) $(GUROBI_PARAMS) -o $(OUTPUT_DIR)/$(ILP_RES_ASSIGNER_OUTPUT_FILE)

ilp-global-solver:
	$(CXX) $(COMMON_FILES) $(ILP_GLOBAL_SOLVER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) $(GUROBI_PARAMS) -o $(OUTPUT_DIR)/$(ILP_GLOBAL_SOLVER_OUTPUT_FILE)