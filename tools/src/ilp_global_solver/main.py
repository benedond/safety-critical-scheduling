#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common import instance
from common import arg_parser
import ilp_global_solver
import json
import logging


if __name__ == "__main__":

    ap = arg_parser.ArgParser()
    input_filename = ap.get_arg_value("--input")

    if input_filename:
        json_data = instance.read_json_from_file(input_filename)
    else:
        json_data = json.load(sys.stdin)

    # parse the instance
    #try:
    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)
    #except:
    #    print("failed to parse input json", file=sys.stderr)

    if ap.is_arg_present("--timelimit"):
        timelimit = float(ap.get_arg_value("--timelimit"))
        logging.info("timelimit was set to {:f}".format(timelimit))
    else:    
        timelimit = float("inf")     

    # solve the instance            
    if ap.is_arg_present("--fixed"):
        solver = ilp_global_solver.SolverFixed(ap, env, acs, timelimit=timelimit)
        solution, tasks = solver.solve()        

        instance.write_solution(json_data, solution)
        instance.write_tasks(json_data, tasks)
    else:
        solver = ilp_global_solver.Solver(ap, env, acs, timelimit=timelimit)
        solution, tasks = solver.solve()        

        instance.write_solution(json_data, solution)
        instance.write_tasks(json_data, tasks)
    

    output_filename = ap.get_arg_value("--output")
    if output_filename:
        instance.write_to_file(json_data, output_filename)
    else:
        json.dump(json_data, sys.stdout, indent=4)
