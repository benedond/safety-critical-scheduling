#!/usr/bin/env python3
import argparse
import os
import sys
import json

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import utils
import random




parser = argparse.ArgumentParser()

parser.add_argument("--bench_file", "-b", type=str, required=True, help="Path to the file describing the benchmarks.")
parser.add_argument("--env_file", "-e", type=str, required=True, help="Path to the environment file.")
parser.add_argument("--char_file", "-c", type=str, help="Path to the benchmark characteristics file.")
parser.add_argument("--out_folder", "-o", type=str, required=True, help="Path to the output folder where the instances will be created.")
parser.add_argument("--window_length", "-w", default=1000, type=int, help="Length of the window in ms.")
parser.add_argument("--seed", "-s", type=int, default=13, help="Random seed.")
parser.add_argument("--n_instances", "-n", type=int, default=1000, help="Number of instances to be generated.")

def get_workload(env, id_to_bench):
    processors_workload = dict()
    
    for p in env["environment"]["processors"]:
        p_name = p["name"]
        processors_workload[p_name] = []
        n_active_cores = random.randint(0, p["processingUnits"])
        
        for c in range(p["processingUnits"]):
            if n_active_cores >= 1 + c:
                b_idx = random.randint(1, len(id_to_bench.keys()) - 1)
            else:
                b_idx = 0
            
            processors_workload[p_name].append(b_idx)                            
    
    return processors_workload


def generate_instance(env, benchmarks_char, id_to_bench, bench_to_cmd, w_len):
    instance = env
    instance["environment"]["majorFrameLength"] = w_len
    workload = get_workload(env, id_to_bench)
    length = w_len
    inst_name = "_".join(map(str,sum(workload.values(), []))) + ".json"
    
    ass_char = []
    tasks = []
    win_tasks = []
    
    task_idx = 0
    for p in env["environment"]["processors"]:
        processor = p["name"]
        p_cores = p["coreIds"]
        
        for c, bench_id in zip(range(len(p_cores)), workload[processor]):                
            core = p_cores[c]
            bench_name = id_to_bench[bench_id]
            bench_cmd = bench_to_cmd[bench_name]
            
            task_name = "{}_{}".format(task_idx, bench_name)
            if bench_name == "sleep":
                cmd = "sleep inf"
                slope = 0
                intercept = 0
            else:
                cmd, slope, intercept = utils.get_cmd_slope_intercept(bench_name, processor, benchmarks_char)
            
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
                            "windows": [{"length": args.window_length, "tasks": win_tasks}]}
    
    return instance, inst_name    


if __name__ == "__main__":      
    args = parser.parse_args()

    random.seed(args.seed)

    if not os.path.exists(args.out_folder):
        os.makedirs(args.out_folder)

    benchmarks = utils.read_csv(args.bench_file)
    env = utils.read_json(args.env_file)
    benchmarks_char = utils.read_csv(args.char_file)   
    
    id_to_bench = dict()
    bench_to_cmd = dict()
    
    # ID 0 is reserved for sleep benchmark
    id_to_bench[0] = "sleep"
    bench_to_cmd["sleep"] = "sleep inf"
    
    next_id = 1
    # save the other benchmarks as well 
    for row in benchmarks.itertuples(index=False):
        id_to_bench[next_id] = row.benchmark
        bench_to_cmd[row.benchmark] = row.command
        next_id += 1
        
    while len(os.listdir(args.out_folder)) < args.n_instances:
        inst, inst_name = generate_instance(env, benchmarks_char, id_to_bench, bench_to_cmd, args.window_length)
        with open(os.path.join(args.out_folder, inst_name), "w") as f:
            f.write(json.dumps(inst, indent=4, sort_keys=True))
                
    # save the mapping as well
    with open(os.path.join(args.out_folder, "mapping.json"), "w") as f:
        f.write(json.dumps(id_to_bench, indent=4, sort_keys=True))
