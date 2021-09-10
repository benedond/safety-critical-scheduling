#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/common/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/decomposed_solver/'))



import instance
import arg_parser
from decomposed_solver import RecoveryModelCP, RecoveryModel, RecoveryModelILPFixed
import numpy as np 
import time
import docplex.cp.modeler as cpmod


if __name__ == "__main__":    
    ap = arg_parser.ArgParser()    
    
    json_data = instance.read_json_from_file("IN_001.json")
    fixed_task_mapping = {}
    # fixed_task_mapping={'task-0': 0, 'task-1': 0, 'task-2': 1, 'task-3': 1, 'task-4': 0}
    
    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)    
    tasks = [ac.task for ac in acs]
    task_to_idx = {t: i for i, t in enumerate(tasks)}       
    
    # Normal recovery model
    solver = RecoveryModel(env, acs,timelimit=float("inf"))
    for t, k_fix in fixed_task_mapping.items():        
        i = task_to_idx[t]            
        solver.model.addConstr(solver.x.sum(i, "*", k_fix) == 1)        
                
    solver.solve()        
    patterns = solver.get_patterns()
    for p in patterns:
        print(p.to_dict())
    obj = sum([p.cost for p in patterns]) / env.major_frame_length
    print(obj)
    print("time", solver.init_time + solver.solving_time)
    
    # ILP fixed recovery model
    solver = RecoveryModelILPFixed(env, acs,timelimit=float("inf"))
    for t, k_fix in fixed_task_mapping.items():        
        i = task_to_idx[t]    
        solver.model.addConstr(solver.a_ikl.sum(i, k_fix, "*") == 1)
                
    solver.solve()        
    patterns = solver.get_patterns()
    for p in patterns:
        print(p.to_dict())    
    obj = sum([p.cost for p in patterns]) / env.major_frame_length
    print(obj)
    print("time", solver.init_time + solver.solving_time)
    