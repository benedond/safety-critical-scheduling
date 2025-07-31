#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from common import instance
import argparse
import qp_lr_ub
import json
import logging

parser = argparse.ArgumentParser()
parser.add_argument("--input", "-i", type=str, default="", help="Path to the input file.")
parser.add_argument("--timelimit", "-t", type=float, default=float("inf"), help="Timelimit.")
parser.add_argument("--output", "-o", type=str, default="", help="Path to the output file.")
parser.add_argument("--path_lr", "-c", type=str, required=True, help="Path to the LR coefficients.")
parser.add_argument("--platform", "-p", type=str, required=True, help="Platform [imx8a, imb8b, tx2].")

def read_json(file):
    f = open(file,"r")        
    data = json.loads(f.read())
    f.close()
    return data

if __name__ == "__main__":
    args = parser.parse_args()

    input_filename = args.input

    if input_filename:
        json_data = instance.read_json_from_file(input_filename)
    else:
        json_data = json.load(sys.stdin)

    timelimit = float(args.timelimit)
    logging.info("timelimit was set to {:f}".format(timelimit))

    # parse the instance
    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)
    
    # parse LR coefficients
    dct = read_json(args.path_lr)
    lr_coeffs = dct[args.platform]
    
    logging.info("Using the following LR coefficients: {}".format(lr_coeffs))
    
    # solve the instance            
    solver = qp_lr_ub.Solver(env, acs, lr_coeffs, timelimit=timelimit)
    solution, tasks = solver.solve()        

    instance.write_solution(json_data, solution)
    instance.write_tasks(json_data, tasks)
    
    output_filename = args.output
    if output_filename:
        instance.write_to_file(json_data, output_filename)
    else:
        json.dump(json_data, sys.stdout, indent=4)
