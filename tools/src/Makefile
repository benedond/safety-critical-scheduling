GUROBI_HOME = /opt/gurobi910/linux64
GUROBI_PARAMS = -I$(GUROBI_HOME)/include -L$(GUROBI_HOME)/lib -lgurobi_g++5.2 -lgurobi91

INCLUDE_DIRS = lib
LINK_DIRS = 

OUTPUT_DIR = ../bin
GENERATOR_OUTPUT_FILE = assignment_generator.exe
P1_GENERATOR_OUTPUT_FILE = instance_generator.exe
SOLVER_OUTPUT_FILE = schedule_solver.exe
GLOBAL_SOLVER_OUTPUT_FILE = global_solver.exe
VISUALISER_OUTPUT_FILE = visualiser.exe
STAT_OUTPUT_FILE = stat.exe
DEMOS_CONFIG_EXPORT_OUTPUT_FILE = demos_config_export.exe
ILP_SOLVER_OUTPUT_FILE = ilp_schedule_solver.exe
ILP_RES_ASSIGNER_OUTPUT_FILE = ilp_assignment_solver.exe
ILP_GLOBAL_SOLVER_OUTPUT_FILE = ilp_global_solver.exe

COMMON_DIR = common
GENERATOR_DIR = assignment_generator
P1_GENERATOR_DIR = instance_generator
VISUALISER_DIR = visualiser
SOLVER_DIR = schedule_solver
GLOBAL_SOLVER_DIR = global_solver
STAT_DIR = stat
DEMOS_CONFIG_EXPORT_DIR = demos_config_export
ILP_SOLVER_DIR = ilp_schedule_solver
ILP_RES_ASSIGNER_DIR = ilp_assignment_solver
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
GENERATOR_FILES = $(GENERATOR_DIR)/main.cpp $(GENERATOR_DIR)/assignment_generator.cpp
P1_GENERATOR_FILES = $(P1_GENERATOR_DIR)/main.cpp $(P1_GENERATOR_DIR)/instance_generator.cpp
SOLVER_FILES = $(SOLVER_DIR)/main.cpp $(SOLVER_DIR)/solver.cpp  $(SOLVER_DIR)/longest_tasks_first_solver.cpp $(SOLVER_DIR)/random_task_order_solver.cpp 
GLOBAL_SOLVER_FILES = $(GLOBAL_SOLVER_DIR)/main.cpp $(GLOBAL_SOLVER_DIR)/global_solver.cpp $(GLOBAL_SOLVER_DIR)/random_global_solver.cpp $(GLOBAL_SOLVER_DIR)/reference_global_solver.cpp $(GLOBAL_SOLVER_DIR)/random_assignment_solver.cpp
VISUALISER_FILES = $(VISUALISER_DIR)/main.cpp $(VISUALISER_DIR)/visualiser.cpp 
STAT_FILES = $(STAT_DIR)/main.cpp
DEMOS_CONFIG_EXPORT_FILES = $(DEMOS_CONFIG_EXPORT_DIR)/main.cpp $(DEMOS_CONFIG_EXPORT_DIR)/demos_config_writer.cpp
ILP_COMMON_FILES = $(COMMON_DIR)/ilp_util.cpp
ILP_SOLVER_FILES = $(ILP_COMMON_FILES) $(ILP_SOLVER_DIR)/main.cpp 
ILP_RES_ASSIGNER_FILES = $(ILP_COMMON_FILES) $(ILP_RES_ASSIGNER_DIR)/main.cpp
ILP_GLOBAL_SOLVER_FILES = $(ILP_COMMON_FILES) $(ILP_GLOBAL_SOLVER_DIR)/main.cpp


.PHONY: assignment_generator instance_generator schedule_solver global_solver visualiser visualiser-display stat demos_config_export ilp_schedule_solver ilp_assignment_solver ilp_global_solver
tools: assignment_generator instance_generator schedule_solver global_solver visualiser stat demos_config_export
all: tools ilp
tools-vd: assignment_generator instance_generator solver visualiser-display stat demos-config-export

assignment_generator: 
	$(CXX) $(COMMON_FILES) $(GENERATOR_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(GENERATOR_OUTPUT_FILE)

instance_generator:
	$(CXX) $(COMMON_FILES) $(P1_GENERATOR_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(P1_GENERATOR_OUTPUT_FILE)	

schedule_solver: 
	$(CXX) $(COMMON_FILES) $(SOLVER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(SOLVER_OUTPUT_FILE)

global_solver:
	$(CXX) $(COMMON_FILES) $(GLOBAL_SOLVER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(GLOBAL_SOLVER_OUTPUT_FILE)

visualiser: 
	$(CXX) $(COMMON_FILES) $(VISUALISER_FILES) lib/lodepng.cpp -Dcimg_display=0 -U__STRICT_ANSI__ $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(VISUALISER_OUTPUT_FILE)

visualiser-display: 
	$(CXX) $(COMMON_FILES) $(VISUALISER_FILES) lib/lodepng.cpp -U__STRICT_ANSI__ $(CXXFLAGS) -lgdi32 $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(VISUALISER_OUTPUT_FILE)

stat: 
	$(CXX) $(COMMON_FILES) $(STAT_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(STAT_OUTPUT_FILE)

demos_config_export:
	$(CXX) $(COMMON_FILES) $(DEMOS_CONFIG_EXPORT_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(DEMOS_CONFIG_EXPORT_OUTPUT_FILE)

ilp: ilp_schedule_solver ilp_assignment_solver ilp_global_solver

ilp_schedule_solver:
	$(CXX) $(COMMON_FILES) $(ILP_SOLVER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) $(GUROBI_PARAMS) -o $(OUTPUT_DIR)/$(ILP_SOLVER_OUTPUT_FILE)

ilp_assignment_solver:
	$(CXX) $(COMMON_FILES) $(ILP_RES_ASSIGNER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) $(GUROBI_PARAMS) -o $(OUTPUT_DIR)/$(ILP_RES_ASSIGNER_OUTPUT_FILE)

ilp_global_solver:
	$(CXX) $(COMMON_FILES) $(ILP_GLOBAL_SOLVER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) $(GUROBI_PARAMS) -o $(OUTPUT_DIR)/$(ILP_GLOBAL_SOLVER_OUTPUT_FILE)