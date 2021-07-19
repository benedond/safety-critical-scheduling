#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common import instance
from common import arg_parser
import decomposed_solver
import json
from typing import List, Tuple, Mapping

# python tools/src/decomposed_solver/main.py --input ./experiments/test_decomposition/IN_20.json 


if __name__ == "__main__":

    ap = arg_parser.ArgParser()
    input_filename = ap.get_arg_value("--input")

    if input_filename:
        json_data = instance.read_json_from_file(input_filename)
    else:
        json_data = json.load(sys.stdin)
    
    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)    

    init_data_path = ap.get_arg_value("--init")    

    if not init_data_path:
        print("No path to initial data was provided.")
        #exit(0)
        
    bap = decomposed_solver.BranchAndPriceSolver(arg_parser, env, acs, init_data_path)
    sol = bap.solve()     
    
