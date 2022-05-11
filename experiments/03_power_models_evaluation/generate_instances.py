#!/usr/bin/env python3
import argparse
import pandas as pd
import json
import random
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import utils

parser = argparse.ArgumentParser()
parser.add_argument("--window_length", default=1000, type=int, help="Length of the window in ms.")
parser.add_argument("--env_file", type=str, help="Path to the environment file.")
parser.add_argument("--char_file", type=str, help="Path to the tasks' characteristics file.")
parser.add_argument("--out_folder", type=str, help="Path to the output folder where the instances will be created.")
parser.add_argument("--seed", default=13, type=int, help="Random seed.")
parser.add_argument("--n_instances", default=1000, type=int, help="Number of instances to be generated.")
parser.add_argument("--scale", default=1.0, type=float, help="Scale of the MF and other time constants.")


def get_workload(env, args, benchmarks):
    processors_workload = {p["name"]: [] for p in env["processors"]}
    
    for p in env["processors"]:
        p_name = p["name"]
        for c in range(p["processingUnits"]):
            if random.random() > 0.5:  # allocate some workload to this core
                b_idx = random.randint(0, len(benchmarks)-1)
                length = max(1,int(round(random.random() * args.window_length * args.scale)))
                processors_workload[p_name].append((benchmarks[b_idx], length))
            else: # core will be empty
                processors_workload[p_name].append(None)
    
    return processors_workload


def workload_is_none(workload):
    for processor in workload.keys():
        for w in workload[processor]:
            if w is not None:
                return False
    return True


def generate_instance(args):
    instance = utils.read_json(args.env_file)
    instance["environment"]["majorFrameLength"] = int(round(args.window_length * args.scale))
    
    benchmarks_char = utils.read_csv(args.char_file)    
    
    workload = {}
    while workload_is_none(workload):
        workload = get_workload(instance["environment"], args, list(benchmarks_char["benchmark"].unique()))

    ass_char = []
    tasks = []
    win_tasks = []
    
    task_idx = 0
    for p in instance["environment"]["processors"]:
        processor = p["name"]
        p_cores = p["coreIds"]
                
        for c, w in zip(range(len(p_cores)), workload[processor]):
            core = p_cores[c]
            if w is None:
                continue
            else:                
                benchmark, length = w
                task_name = "{}_{}".format(task_idx, benchmark)
                cmd, slope, intercept = utils.get_cmd_slope_intercept(benchmark, processor, benchmarks_char)
                
                cmd = 'TB_OPTS="--count=0 --work_done_every_sec=0.5 --work_done_str=CPU{}_work_done" '.format(core) + cmd
                
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
                                  "processingUnit": c,
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
                            "windows": [{"length": int(round(args.window_length * args.scale)), "tasks": win_tasks}]}
    
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
