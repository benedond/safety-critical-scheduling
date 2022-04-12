#! /usr/bin/python3

import sys
import os
import json
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '../tools/src/common'))
import instance

lr_coefficients = {
	"imx8a": {"A53": {"slope": 1.252, "intercept": 0.273},    "A72": {"slope": 0.484, "intercept": 0.529}},
    "imx8b": {"A53": {"slope": 1.133, "intercept": 0.234},    "A72": {"slope": 0.413, "intercept": 0.526}},
    "tx2":   {"A72": {"slope": 0.000, "intercept": 0.000}, "Denver": {"slope": 0.000, "intercept": 0.000}}
}

if __name__ == "__main__":
    assert len(sys.argv) >= 3, "path_in and path_out need to be present"

    path_in = sys.argv[1]
    path_out = sys.argv[2]

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
        
        solver_name_inst = f[f.find("-")+1:-4]

        with open(os.path.join(path_in,f),"r") as f_in:
            data = json.load(f_in)

            inst_name = f.split(".")[0]
            solver_name = data["solution"]["solverName"]
            solution_time = data["solution"]["solutionTime"]
            n_tasks = len(data["assignmentCharacteristics"])
            sol_len = instance.get_solution_length(instance.parse_solution(data))
            obj_sm = instance.get_solution_objective(data)
            obj_lr_ub = instance.get_solution_objective_lr_ub(data, lr_coefficients["imx8a"])
            obj_lr = instance.get_solution_objective_lr(data, lr_coefficients["imx8a"])
            
            all_data["instance"].append(inst_name)
            all_data["solver"].append(solver_name)
            all_data["time"].append(solution_time)
            all_data["n"].append(n_tasks)
            all_data["len"].append(sol_len)
            all_data["obj_sm"].append(obj_sm)
            all_data["obj_lr_ub"].append(obj_lr_ub)
            all_data["obj_lr"].append(obj_lr)
            
    df = pd.DataFrame(all_data)
    df.to_csv(path_out, index=False)

