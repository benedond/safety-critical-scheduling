#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from common import instance
import ilp_sm_i
import json
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input", "-i", type=str, default="", help="Path to the input file.")
parser.add_argument("--timelimit", "-t", type=float, default=float("inf"), help="Timelimit.")
parser.add_argument("--output", "-o", type=str, default="", help="Path to the output file.")
parser.add_argument("--optimize", action='store_true', help="Optimize the schedule.")
parser.add_argument("--iis", action='store_true', help="Compute IIS.")

if __name__ == "__main__":
    args = parser.parse_args()
    input_filename = args.input

    if input_filename:
        json_data = instance.read_json_from_file(input_filename)
    else:
        json_data = json.load(sys.stdin)

    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)
    
    timelimit = float(args.timelimit)
    logging.info("timelimit was set to {:f}".format(timelimit)) 

    solver = ilp_sm_i.Solver(args, env, acs, timelimit=timelimit)
    solution, tasks = solver.solve()        

    instance.write_solution(json_data, solution)
    instance.write_tasks(json_data, tasks)

    output_filename = args.output
    if output_filename:
        instance.write_to_file(json_data, output_filename)
    else:
        json.dump(json_data, sys.stdout, indent=4)
