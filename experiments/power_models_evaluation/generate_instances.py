#!/usr/bin/env python3
import argparse
import pandas as pd
import json
import random
import os

parser = argparse.ArgumentParser()
parser.add_argument("--window_length", default=1000, type=int, help="Length of the window in ms.")
parser.add_argument("--env_file", type=str, help="Path to the environment file.")
parser.add_argument("--char_file", type=str, help="Path to the tasks' characteristics file.")
parser.add_argument("--out_folder", type=str, help="Path to the output folder where the instances will be created.")
parser.add_argument("--seed", default=13, type=int, help="Random seed.")
parser.add_argument("--n_instances", default=1000, type=int, help="Number of instances to be generated.")


cores_offset = {"A53": [0, 1, 2, 3],
                "A72": [4, 5],
                "A57": [0, 3, 4, 5],
                "Denver": [1, 2]}

cores = {"A53": [0, 1, 2, 3],
          "A72": [0, 1],
          "A57": [0, 1, 2, 3],
          "Denver": [0, 1]}

def read_json(file):
    f = open(file,"r")        
    data = json.loads(f.read())
    f.close()
    return data


def read_csv(file):
    return pd.read_csv(file, comment="#")    


def get_workload(env, args, benchmarks):
    processors_workload = {p["name"]: [] for p in env["processors"]}
    
    for p_name in processors_workload.keys():
        for c in cores[p_name]:
            if random.random() > 0.5:  # allocate some workload to this core
                b_idx = random.randint(0, len(benchmarks)-1)
                length = int(round(random.random() * args.window_length))                
                processors_workload[p_name].append((benchmarks[b_idx], length))
            else: # core will be empty
                processors_workload[p_name].append(None)
    
    return processors_workload


def get_cmd_slope_intercept(benchmark, processor, df):
    row = df[ (df["benchmark"] == benchmark) & (df["affinity"] == processor) ].iloc[0]
    return row["command"], row["slope"], row["intercept"]


def workload_is_none(workload):
    for processor in workload.keys():
        for w in workload[processor]:
            if w is not None:
                return False
    return True


def generate_instance(args):
    instance = read_json(args.env_file)
    instance["environment"]["majorFrameLength"] = args.window_length
    
    benchmarks_char = read_csv(args.char_file)    
    
    workload = {}
    while workload_is_none(workload):
        workload = get_workload(instance["environment"], args, list(benchmarks_char["benchmark"].unique()))

    ass_char = []
    tasks = []
    win_tasks = []
    
    task_idx = 0
    for p_idx, processor in enumerate(workload.keys()):
        for core, w in zip(cores[processor], workload[processor]):
            if w is None:
                continue
            else:                
                benchmark, length = w
                task_name = "{}_{}".format(task_idx, benchmark)
                cmd, slope, intercept = get_cmd_slope_intercept(benchmark, processor, benchmarks_char)
                
                cmd = 'TB_OPTS="--count=0 --work_done_every_sec=0.5 --work_done_str=CPU{}_work_done" '.format(cores_offset[processor][core]) + cmd
                
                # Prepare assignment characteristics
                ass_char.append({"command": cmd,
                                 "task": task_name,
                                 "resourceAssignments": [{"length": length,
                                                          "slope": slope,
                                                          "intercept": intercept,
                                                          "processors": [{"processingUnits": 1, "processor": processor}]
                                                          }]
                                })
                
                # Prepare resource assignment
                tasks.append({"assignmentIndex": 0,
                               "command": cmd,
                               "length": length,
                               "name": task_name,
                               "processors": [{"processor": processor, "processingUnits": 1}]
                               })
                
                win_tasks.append({"length": length,
                                  "processingUnit": core,
                                  "processor": processor,
                                  "start": 0,
                                  "task": task_name})
                
                task_idx += 1
                
    instance["assignmentCharacteristics"] = ass_char
    instance["tasks"] = tasks
    instance["solution"] = {"feasible": True,
                            "solutionTime": 0,
                            "solverMetadata": None,
                            "solverName": "RandomGenerator",
                            "windows": [{"length": args.window_length, "tasks": win_tasks}]}
    
    return instance                

if __name__ == "__main__":      
    args = parser.parse_args()
    random.seed(args.seed)
    
    if not os.path.exists(args.out_folder):
        os.makedirs(args.out_folder)
        
    for i in range(args.n_instances):
        inst = generate_instance(args)
        
        with open(os.path.join(args.out_folder, "inst_{:04d}.json".format(i)), "w") as f:
            f.write(json.dumps(inst, indent=4, sort_keys=True))