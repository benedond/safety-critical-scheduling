#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/common/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/ilp_fixed_solver/'))



import instance
import arg_parser
from ilp_fixed_solver import SolverSupport
import numpy as np 
import time
import docplex.cp.modeler as cpmod


if __name__ == "__main__":    
    ap = arg_parser.ArgParser()
    json_data = instance.read_json_from_file("IN_001.json")
    fixed_task_mapping={'task-12': 0, 'task-16': 0, 'task-2': 0, 'task-19': 0, 'task-5': 0, 'task-1': 0, 'task-14': 0, 'task-22': 0, 'task-7': 0, 'task-21': 0, 'task-4': 0, 'task-27': 0, 'task-25': 0, 'task-24': 0, 'task-10': 0, 'task-13': 0, 'task-23': 0, 'task-26': 0, 'task-8': 0, 'task-0': 0, 'task-6': 0, 'task-15': 0, 'task-20': 0, 'task-9': 0, 'task-17': 0, 'task-3': 0}
    
    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)    
    tasks = [ac.task for ac in acs]
    task_to_idx = {t: i for i, t in enumerate(tasks)}       
    
    solver = SolverSupport(ap, env, acs, {"task-0": 0, "task-1": 0, "task-2": 0})
    sol, tasks = solver.solve()
    
    print(sol.to_dict())
    for t in tasks:
        print(t.to_dict())

    
    