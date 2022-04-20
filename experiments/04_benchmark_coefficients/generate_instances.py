#!/usr/bin/env python3
import argparse
import pandas as pd
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import utils
import json

parser = argparse.ArgumentParser()
parser.add_argument("--window_length", "-w", default=1000, type=int, help="Length of the window in ms.")
parser.add_argument("--env_file", "-e", type=str, required=True, help="Path to the environment file.")
parser.add_argument("--bench_file", "-b", type=str, required=True, help="Path to the benchmarks file.")
parser.add_argument("--out_folder", "-o", type=str, required=True, help="Path to the output folder where the instances will be created.")


def generate_instance(args, benchmark, cmd, processor, cover_all):    
    instance = utils.read_json(args.env_file)    
    instance["environment"]["majorFrameLength"] = args.window_length
    length = args.window_length    
    p_name = processor["name"]    
                    
    ass_char = []
    tasks = []
    win_tasks = []
    
    core_ids = processor["coreIds"] if cover_all else [processor["coreIds"][0]]
    for core_enum, c in enumerate(core_ids):
        task_name = "{}_{}".format(c, benchmark)
        slope, intercept = 0, 0
                
        cmd_str = 'TB_OPTS="--count=0 --work_done_every_sec=0.5 --work_done_str=CPU{}_work_done" '.format(c) + cmd
                
        # Prepare assignment characteristics
        ass_char.append({"command": cmd_str,
                         "task": task_name,
                         "resourceAssignments": [{"length": length,
                                                  "slope": slope,
                                                  "intercept": intercept,
                                                  "processors": [{"processingUnits": 1, "processor": p_name}]
                                                  }]
                        })
        
        # Prepare resource assignment
        tasks.append({"assignmentIndex": 0,
                      "command": cmd_str,
                      "length": length,
                      "name": task_name,
                      "processors": [{"processor": p_name, "processingUnits": 1}]
                     })
        
        win_tasks.append({"length": length,
                          "processingUnit": core_enum,
                          "processor": p_name,
                          "start": 0,
                          "task": task_name})
                
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
    
    if not os.path.exists(args.out_folder):
        os.makedirs(args.out_folder)

    benchmarks = utils.read_csv(args.bench_file)
    env = utils.read_json(args.env_file)
     
    for row in benchmarks.itertuples(index=False):
        bench_name = row.benchmark
        bench_cmd = row.command 
    
        for p_idx, processor in enumerate(env["environment"]["processors"]):
            p_name = processor["name"]
                    
            inst_1 = generate_instance(args, bench_name, bench_cmd, processor, False)
            with open(os.path.join(args.out_folder, "{}_{}_one.json".format(bench_name, p_name)), "w") as f:
                f.write(json.dumps(inst_1, indent=4, sort_keys=True))    
            
            inst_all = generate_instance(args, bench_name, bench_cmd, processor, True)
            with open(os.path.join(args.out_folder, "{}_{}_all.json".format(bench_name, p_name)), "w") as f:
                f.write(json.dumps(inst_all, indent=4, sort_keys=True))  
            