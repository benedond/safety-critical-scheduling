GUROBI_HOME = /opt/gurobi910/linux64
GUROBI_PARAMS = -I$(GUROBI_HOME)/include -L$(GUROBI_HOME)/lib -lgurobi_g++5.2 -lgurobi91

INCLUDE_DIRS = lib
LINK_DIRS = 

OUTPUT_DIR = ../bin
P1_GENERATOR_OUTPUT_FILE = instance_generator.exe
SOLVER_OUTPUT_FILE = schedule_solver.exe
VISUALISER_OUTPUT_FILE = visualizer.exe
DEMOS_CONFIG_EXPORT_OUTPUT_FILE = demos_config_export.exe
ILP_RES_ASSIGNER_OUTPUT_FILE = assignment_solver.exe
ILP_GLOBAL_SOLVER_OUTPUT_FILE = ilp_global_solver.exe

COMMON_DIR = common

P1_GENERATOR_DIR = instance_generator
SOLVER_DIR = schedule_solver
VISUALISER_DIR = visualizer
DEMOS_CONFIG_EXPORT_DIR = demos_config_export
ILP_RES_ASSIGNER_DIR = assignment_solver
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

P1_GENERATOR_FILES = $(P1_GENERATOR_DIR)/main.cpp $(P1_GENERATOR_DIR)/instance_generator.cpp
SOLVER_FILES = $(SOLVER_DIR)/main.cpp $(SOLVER_DIR)/solver.cpp  $(SOLVER_DIR)/longest_tasks_first_solver.cpp $(SOLVER_DIR)/random_task_order_solver.cpp 
VISUALISER_FILES = $(VISUALISER_DIR)/main.cpp $(VISUALISER_DIR)/visualizer.cpp 
DEMOS_CONFIG_EXPORT_FILES = $(DEMOS_CONFIG_EXPORT_DIR)/main.cpp $(DEMOS_CONFIG_EXPORT_DIR)/demos_config_writer.cpp
ILP_COMMON_FILES = $(COMMON_DIR)/ilp_util.cpp
ILP_RES_ASSIGNER_FILES = $(ILP_COMMON_FILES) $(ILP_RES_ASSIGNER_DIR)/main.cpp $(ILP_RES_ASSIGNER_DIR)/assignment_solver.cpp
ILP_GLOBAL_SOLVER_FILES = $(ILP_COMMON_FILES) $(ILP_GLOBAL_SOLVER_DIR)/main.cpp $(ILP_GLOBAL_SOLVER_DIR)/ilp_global_solver.cpp


.PHONY: instance_generator schedule_solver visualizer visualizer-display demos_config_export assignment_solver ilp_global_solver
all: instance_generator schedule_solver visualizer demos_config_export assignment_solver ilp_global_solver

instance_generator:
	$(CXX) $(COMMON_FILES) $(P1_GENERATOR_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(P1_GENERATOR_OUTPUT_FILE)	

schedule_solver: 
	$(CXX) $(COMMON_FILES) $(SOLVER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(SOLVER_OUTPUT_FILE)

visualizer: 
	$(CXX) $(COMMON_FILES) $(VISUALISER_FILES) lib/lodepng.cpp -Dcimg_display=0 -U__STRICT_ANSI__ $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(VISUALISER_OUTPUT_FILE)

visualizer-display: 
	$(CXX) $(COMMON_FILES) $(VISUALISER_FILES) lib/lodepng.cpp -U__STRICT_ANSI__ $(CXXFLAGS) -lgdi32 $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(VISUALISER_OUTPUT_FILE)

demos_config_export:
	$(CXX) $(COMMON_FILES) $(DEMOS_CONFIG_EXPORT_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) -o $(OUTPUT_DIR)/$(DEMOS_CONFIG_EXPORT_OUTPUT_FILE)

assignment_solver:
	$(CXX) $(COMMON_FILES) $(ILP_RES_ASSIGNER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) $(GUROBI_PARAMS) -o $(OUTPUT_DIR)/$(ILP_RES_ASSIGNER_OUTPUT_FILE)

ilp_global_solver:
	$(CXX) $(COMMON_FILES) $(ILP_GLOBAL_SOLVER_FILES) $(CXXFLAGS) $(RELEASE_FLAGS) $(GUROBI_PARAMS) -o $(OUTPUT_DIR)/$(ILP_GLOBAL_SOLVER_OUTPUT_FILE)