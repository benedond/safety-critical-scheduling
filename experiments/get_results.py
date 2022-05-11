#! /usr/bin/python3

import argparse
import sys
import os
import json
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '../tools/src/common'))
import instance
import utils

parser = argparse.ArgumentParser()
parser.add_argument("--lr_coeffs_file", "-l", type=str, required=True, help="Path to the file with LR coefficients.")
parser.add_argument("--path_in",   "-i", type=str, required=True, help="Input folder.")
parser.add_argument("--path_out",  "-o", type=str, required=True, help="Output file path.")
parser.add_argument("--platform",  "-p", type=str, required=True, help="Platform name (imx8a, imx8b, tx2).")
parser.add_argument("--skip",  "-s", type=str, default="", help="Filename to skip.")

if __name__ == "__main__":
    args = parser.parse_args()
    path_in = args.path_in
    path_out = args.path_out
    
    utils.create_folder(os.path.dirname(path_out))

    lr_coefficients = utils.read_json(args.lr_coeffs_file)

    all_data = {"instance": [],
                "solver": [],
                "time": [],
                "n": [],
                "len": [],
                "obj_sm": [],
                "obj_lr_ub": [],
                "obj_lr": []}

    for f in os.listdir(path_in):        
        # if not f.endswith(".out"):
        #     continue
        if f == args.skip:
            continue
        solver_name_inst = f[f.find("-")+1:-4]

        with open(os.path.join(path_in,f),"r") as f_in:
            data = json.load(f_in)

            inst_name = f.split(".")[0]
            solver_name = data["solution"]["solverName"]
            solution_time = data["solution"]["solutionTime"]
            n_tasks = len(data["assignmentCharacteristics"])
            sol_len = instance.get_solution_length(instance.parse_solution(data))
            obj_sm = instance.get_solution_objective(data)
            obj_lr_ub = instance.get_solution_objective_lr_ub(data, lr_coefficients[args.platform])
            obj_lr = instance.get_solution_objective_lr(data, lr_coefficients[args.platform])
            
            all_data["instance"].append(inst_name)
            all_data["solver"].append(solver_name)
            all_data["time"].append(solution_time)
            all_data["n"].append(n_tasks)
            all_data["len"].append(sol_len)
            all_data["obj_sm"].append(obj_sm)
            all_data["obj_lr_ub"].append(obj_lr_ub)
            all_data["obj_lr"].append(obj_lr)

    df = pd.DataFrame(all_data)
    df = df.sort_values("instance")
    df.to_csv(path_out, index=False)

