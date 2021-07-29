#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common import instance
from common import arg_parser
import decomposed_solver
import json
from typing import List, Tuple, Mapping
import logging

# python tools/src/decomposed_solver/main.py --input ./experiments/test_decomposition/IN_20.json 


if __name__ == "__main__":


    # Problematic example with 5 tasks, branching is ambiguous
    #[('task-3', 'task-4'), ('task-1', 'task-0'), ('task-1', 'task-2'), ('task-0', 'task-2')], on diff = [('task-3', 'task-1'), ('task-3', 'task-0'), ('task-3', 'task-2'), ('task-1', 'task-4'), ('task-4', 'task-0'), ('task-4', 'task-2')]
    # mm = decomposed_solver.MasterModel([
    #     instance.Pattern(18.152188598995025, 16, {'task-3': 1, 'task-4': 0}),
    #     instance.Pattern(252.35088519544485, 70, {'task-0': 0, 'task-1': 1, 'task-2': 0}),
    #     instance.Pattern(122.1437022103734, 88, {'task-0': 0, 'task-1': 0, 'task-2': 1}),
    #     instance.Pattern(139.84092026697834, 75, {'task-0': 1, 'task-1': 0, 'task-2': 0})], 95, ["task-0", "task-1", "task-2", "task-3", "task-4"])

    # mm.solve()

    # for i in range(len(mm.alpha)):
    #     print(mm.alpha[i].X)

    # print("is int?", mm.is_solution_integer())

    # exit(0)
        

    ap = arg_parser.ArgParser()
    input_filename = ap.get_arg_value("--input")

    if input_filename:
        json_data = instance.read_json_from_file(input_filename)
    else:
        json_data = json.load(sys.stdin)
    
    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)    

    if ap.is_arg_present("--log"): # needs to apprea before calling any logging
        logging.basicConfig(level=logging.INFO)        
    else:
        logging.basicConfig(level=logging.ERROR)

    if ap.is_arg_present("--init"):
        init_data_path = ap.get_arg_value("--init")
    else:    
        init_data_path = None
        logging.info("No path to initial data was provided.")    
        
    if ap.is_arg_present("--timelimit"):
        timelimit = float(ap.get_arg_value("--timelimit"))
        logging.info("timelimit was set to {:f}".format(timelimit))
    else:    
        timelimit = float("inf")        
        
    bap = decomposed_solver.BranchAndPriceSolver(ap, env, acs, init_data_path, timelimit=timelimit)
    solution, tasks = bap.solve()

    instance.write_solution(json_data, solution)
    instance.write_tasks(json_data, tasks)

    output_filename = ap.get_arg_value("--output")
    if output_filename:
        instance.write_to_file(json_data, output_filename)
    else:
        json.dump(json_data, sys.stdout, indent=4)
 
    
