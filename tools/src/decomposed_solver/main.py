#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common import instance
from common import arg_parser
import decomposed_solver
import json


if __name__ == "__main__":

    ap = arg_parser.ArgParser()
    input_filename = ap.get_arg_value("--input")

    if input_filename:
        json_data = instance.read_json_from_file(input_filename)
    else:
        json_data = json.load(sys.stdin)
    
    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)    

    init_data = instance.read_json_from_file("/home/benedond/Doktorat/Vyzkum/Projects/safety-critical-scheduling/experiments/test_decomposition/IN_20_solution.json")
    patterns = instance.get_patterns(init_data)
    for p in patterns:
        print(p.to_dict())
        
    mm = decomposed_solver.MasterModel(patterns, env.major_frame_length, [ac.task for ac in acs])
    mm.solve()
    pi0, pit = mm.get_dual_prices()
    
    print(mm.)

    # # solve    
    # solver = decomposed_solver(ap, env, acs)
    # solution, tasks = solver.solve()        

    # instance.write_solution(json_data, solution)
    # instance.write_tasks(json_data, tasks)    

    # output_filename = ap.get_arg_value("--output")
    # if output_filename:
    #     instance.write_to_file(json_data, output_filename)
    # else:
    #     json.dump(json_data, sys.stdout, indent=4)
