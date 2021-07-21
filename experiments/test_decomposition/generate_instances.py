import sys
import os
from numpy import random as rnd
import json

def generate_instance(path: str, n_tasks: int):
    inst = {}
    
    total_A53 = 0
    total_A72 = 0
    
    ac = []
    for i in range(n_tasks):
        proc_A53 = rnd.randint(1,100)
        proc_A72 = rnd.randint(1,100)
        
        total_A53 += proc_A53
        total_A72 += proc_A72
        
        task_ac = {"command": "",
                   "task": "task-{:d}".format(i),
                   "resourceAssignments": [
                       {
                           "slope": rnd.random(),
                           "intercept": rnd.random(),
                           "length": proc_A53,
                           "processors": [{"processingUnits": 1,
                                           "processor": "A53"}],
                       },
                       {
                           "slope": rnd.random(),
                           "intercept": rnd.random(),
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
    
    h_coef = rnd.random() * 0.7 + 0.8  # [0.8, 1.5)
    
    inst["environment"] = {"majorFrameLength": int(round(total_A53 / units_A53 * h_coef)),
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
        
    rnd.seed(13)
        
    dest = sys.argv[1]
    n_tasks = int(sys.argv[2])
    n_inst =  int(sys.argv[3])
    
    for i in range(n_inst):
        generate_instance(os.path.join(dest, "IN_{:03d}.json".format(i)), n_tasks)
    
    
    
    
