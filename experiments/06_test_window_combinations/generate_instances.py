#!/usr/bin/env python3
import argparse
import pandas as pd
import json
import random
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import utils
from enum import Enum

class InstanceType(Enum):
    FIRST_CLUSTER = 1
    SECOND_CLUSTER = 2
    BOTH_CLUSTERS = 3
    MIX_FIRST = 4
    MIX_SECOND = 5

experiment_type = ["single", "all"]

parser = argparse.ArgumentParser()
parser.add_argument("--window_length", default=500, type=int, help="Length of the window in ms.")
parser.add_argument("--env_file", type=str, help="Path to the environment file.")
parser.add_argument("--char_file", type=str, help="Path to the tasks' characteristics file.")
parser.add_argument("--out_folder", type=str, help="Path to the output folder where the instances will be created.")
parser.add_argument("--seed", default=13, type=int, help="Random seed.")
parser.add_argument("--n_instances", default=10, type=int, help="Number of instances to be generated.")
parser.add_argument("--experiment_type", default="single", type=str, choices=experiment_type, help="Type of the experiment - whether to generate a single core for each cluster, or all cores.")


def get_benchmarks(env, benchmarks):
    processors_workload = {p["name"]: None for p in env["processors"]}
    
    for k in processors_workload.keys():
        processors_workload[k] = benchmarks[random.randint(0, len(benchmarks)-1)]
        
    return processors_workload


def generate_instance(args, benchmarks, inst_type):
    instance = utils.read_json(args.env_file)
    w_len = int(args.window_length * 2 if inst_type in [InstanceType.MIX_FIRST, InstanceType.MIX_SECOND] else args.window_length)
    instance["environment"]["majorFrameLength"] = w_len
    
    benchmarks_char = utils.read_csv(args.char_file)    
    
    ass_char = []
    tasks = []
    win_tasks = []
    
    task_idx = 0
    for p in instance["environment"]["processors"]:
        processor = p["name"]
        p_cores = p["coreIds"]
                
        for c in range(len(p_cores)):
            core = p_cores[c]
            
            if c > 0 and args.experiment_type == "single": # skip all other cores 
                continue
            elif inst_type == InstanceType.FIRST_CLUSTER and processor == instance["environment"]["processors"][1]["name"]: # skip the second cluster
                continue
            elif inst_type == InstanceType.SECOND_CLUSTER and processor == instance["environment"]["processors"][0]["name"]: # skip the first cluster
                continue
            else:                            
                benchmark = benchmarks[processor]
                length = args.window_length
                
                if inst_type == InstanceType.MIX_FIRST and processor == instance["environment"]["processors"][0]["name"]:
                    length *= 2
                elif inst_type == InstanceType.MIX_SECOND and processor == instance["environment"]["processors"][1]["name"]:
                    length *= 2
                                
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
                            "windows": [{"length": w_len, "tasks": win_tasks}]}
    
    return instance                

if __name__ == "__main__":      
    args = parser.parse_args()
    random.seed(args.seed)
    
    if not os.path.exists(args.out_folder):
        os.makedirs(args.out_folder)

    instance = utils.read_json(args.env_file)        
    benchmarks_char = utils.read_csv(args.char_file)    
    
    benchmarks = [get_benchmarks(instance["environment"], list(benchmarks_char["benchmark"].unique())) for i in range(args.n_instances)]
        
    for i in range(args.n_instances):
        bench = benchmarks[i]
        
        for inst_type in InstanceType:
            inst = generate_instance(args, bench, inst_type)
            with open(os.path.join(args.out_folder, "inst_{:04d}_{}_{}.json".format(i, args.experiment_type, inst_type.name.lower())), "w") as f:
                f.write(json.dumps(inst, indent=4, sort_keys=True))
                
