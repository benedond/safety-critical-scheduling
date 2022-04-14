#!/usr/bin/env python3
import argparse
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import utils

parser = argparse.ArgumentParser()
parser.add_argument("--window_length", "-w", default=1000, type=int, help="Length of the window in ms.")
parser.add_argument("--env_file", "-e", type=str, help="Path to the environment file.")
parser.add_argument("--bench_file", "-b", type=str, help="Path to the benchmarks file.")
parser.add_argument("--out_folder", "-o", type=str, help="Path to the output folder where the instances will be created.")


def generate_instance(args, benchmark, processor, cover_all):
    instance = read_json(args.env_file)
    instance["environment"]["majorFrameLength"] = args.window_length
    
    # TODO: write the generator
    
    workload = {}
    while workload_is_none(workload):
        workload = get_workload(instance["environment"], args, list(benchmarks["benchmark"].unique()))

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
                            "windows": [{"length": int(round(args.window_length * args.scale)), "tasks": win_tasks}]}
    
    return instance                

if __name__ == "__main__":      
    args = parser.parse_args()
    random.seed(args.seed)
    
    if not os.path.exists(args.out_folder):
        os.makedirs(args.out_folder)

    benchmarks = utils.read_csv(args.bench_file)
    env = utils.read_json(args.env_file)
    
    for benchmark in benchmarks["benchmark"].unique():
        for p in env["processors"]:
            p_name = p["name"]
            
            inst_1 = generate_instance(benchmark, p_name, False)
            with open(os.path.join(args.out_folder, "{}_{}_one.json".format(benchmark, p_name)), "w") as f:
                f.write(json.dumps(inst_1, indent=4, sort_keys=True))    
            
            inst_all = generate_instance(benchmark, p_name, True)
            with open(os.path.join(args.out_folder, "{}_{}_all.json".format(benchmark, p_name)), "w") as f:
                f.write(json.dumps(inst_all, indent=4, sort_keys=True))  
        