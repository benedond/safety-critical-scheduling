#!/usr/bin/env python3

import sys
import os
from numpy import random as rnd
import json

def generate_instance(path: str, n_tasks: int, real_dependencies=False):
    inst = {}
    
    total_A53 = 0
    total_A72 = 0
    
    ac = []
    for i in range(n_tasks):
        if not real_dependencies:
            proc_A53 = rnd.randint(1,100)
            proc_A72 = rnd.randint(1,100)
        else:  # if real_dependencies, scale A53 processing time accordingly
            A53_A72_ratio = rnd.random() * 2.8 + 0.8  # [0.8, 3.6)
            proc_A72 = rnd.randint(1,100)
            proc_A53 = int(round(proc_A72 * A53_A72_ratio))
            
        total_A53 += proc_A53
        total_A72 += proc_A72
        
        if not real_dependencies:
            A53_slope = rnd.random()
            A53_intercept = rnd.random()            
            A72_slope = rnd.random()
            A72_intercept = rnd.random()
        else:
            # Just random guess
            #A53_A72_slope_ratio = rnd.random() * 2 + 0.5  # [0.5, 2.5)
            #A53_A72_intercept_ratio = rnd.random() * 5.6 + 1.4  # [1.4, 7)
            # Inferred from data
            A53_A72_slope_ratio = 2.07*(proc_A53/proc_A72) - 0.20 + (rnd.random()*1.6 - 0.8)  # 2.07 * proc_ratio -0.2 + rnd.noise([-0.8,0.8])
            A53_A72_intercept_ratio = 0.08*(proc_A53/proc_A72) + 0.75 + (rnd.random() - 0.5)  # 0.08 * proc_ratio + 0.75 + rnd.noise([-0.5,0.5])
            
            
            if A53_A72_slope_ratio < 0 or A53_A72_intercept_ratio < 0:
                print("Warning - ratio < 0.")
            
            A53_slope = rnd.random()*0.36 + 0.17  # [0.17,0.53]
            A53_intercept = rnd.random()*1.3 + 0.2  # [0.2, 1.5]
            A72_slope = A53_slope * A53_A72_slope_ratio
            A72_intercept = A53_intercept * A53_A72_intercept_ratio            
        
        task_ac = {"command": "",
                   "task": "task-{:d}".format(i),
                   "resourceAssignments": [
                       {
                           "slope": A53_slope,
                           "intercept": A53_intercept,
                           "length": proc_A53,
                           "processors": [{"processingUnits": 1,
                                           "processor": "A53"}],
                       },
                       {
                           "slope": A72_slope,
                           "intercept": A72_intercept,
                           "length": proc_A72,
                           "processors": [{"processingUnits": 1,
                                           "processor": "A72"}],
                       }
                       ]
                   }
        ac.append(task_ac)
    inst["assignmentCharacteristics"] = ac
    
    units_A53 = rnd.randint(1,5)
    units_A72 = rnd.randint(1,5)
    
    if not real_dependencies:
        h_coef = rnd.random() * 0.7 + 0.8  # [0.8, 1.5)
        mf_len = int(round(total_A53 / units_A53 * h_coef))
    else:  # if real real_dependencies, 
        h_coef = rnd.random() * 2.2 + 0.8  # [0.8, 3)
        mf_len = int(round(total_A72 / units_A72 * h_coef))
    
    inst["environment"] = {"majorFrameLength": mf_len,
                           "problemVersion": 1,
                           "processors": [{"name": "A53",
                                           "processingUnits": units_A53,
                                           "type": "main_processor"},
                                          {"name": "A72",
                                           "processingUnits": units_A72,
                                           "type": "main_processor"}
                                          ],
                           "scPart": 1.0
                           }
    
    json.dump(inst, open(path, "w"), indent=4)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Fist argument should be destination path.")
        print("Second argument should be number of tasks.")
        print("Third argument should be number of instances to generate.")
        exit(0)
    
    dest = sys.argv[1]
    n_tasks = int(sys.argv[2])
    n_inst =  int(sys.argv[3])
    
    if len(sys.argv) > 4:
        arg_v = sys.argv[4].lower()
        if arg_v not in ["true", "false"]:
            print("Fourth argument should be either 'true' or 'false'")
        
        real_dependencies = False if sys.argv[4].lower() == "false" else True
        print("Real dependencies set to:", real_dependencies)
    else:
        real_dependencies = False
    
    rnd.seed(13)
            
    if not os.path.exists(dest):
        os.makedirs(dest)
        
        with open(os.path.join(dest,"gurobi.env"), "w") as f:
            f.write("Threads 1\n")
            f.write("OutputFlag 0\n")
            f.write("TimeLimit 600\n")
            
        with open(os.path.join(dest,"RUN.sh"), "w") as f:
            f.write("#!/bin/bash\n")
            f.write("for i in *.json\n")
            f.write("do\n")
            f.write("    echo $i\n")
            f.write("    if [ ! -f $i-global.out ]; then\n")
            f.write("        ../../../tools/src/ilp_global_solver/main.py --input $i --output $i-global.out --fixed --timelimit 600 2> $i-global.err 1> $i-global.log\n")
            f.write("        ../../../tools/bin/visualizer.exe --input $i-global.out --output $i-global.png\n")
            f.write("    fi \n")
            f.write("    if [ ! -f $i-bap.out ]; then\n")
            f.write("        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap.out --log --branching supports --timelimit 600 2> $i-bap.err 1> $i-bap.log\n")
            f.write("        ../../../tools/bin/visualizer.exe --input $i-bap.out --output $i-bap.png\n")
            f.write("    fi \n")
            f.write("    if [ ! -f $i-bap-task.out ]; then\n")
            f.write("        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap-task.out --log --branching tasks --timelimit 600 2> $i-bap-task.err 1> $i-bap-task.log\n")
            f.write("        ../../../tools/bin/visualizer.exe --input $i-bap-task.out --output $i-bap-task.png\n")
            f.write("    fi \n")
            f.write("done")

    for i in range(n_inst):
        generate_instance(os.path.join(dest, "IN_{:03d}.json".format(i)), n_tasks, real_dependencies=real_dependencies)
    
    
    
    
