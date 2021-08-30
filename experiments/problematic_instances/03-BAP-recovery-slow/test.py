#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/common/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/decomposed_solver/'))
#sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/ilp_fixed_solver/'))


import instance
import arg_parser
from decomposed_solver import RecoveryModel
import ilp_fixed_solver
import numpy as np 



if __name__ == "__main__":    
    ap = arg_parser.ArgParser()
    json_data = instance.read_json_from_file("IN_015.json")
    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)    
    tasks = [ac.task for ac in acs]
    task_to_idx = {t: i for i, t in enumerate(tasks)} 


    # # Try with fixed assignment:
    # fixed_task_mapping={'task-12': 0, 'task-16': 0, 'task-2': 0, 'task-19': 0, 'task-5': 0, 'task-1': 0, 'task-14': 0, 'task-22': 0, 'task-7': 0, 'task-21': 0, 'task-4': 0, 'task-27': 0, 'task-25': 0, 'task-24': 0, 'task-10': 0, 'task-13': 0, 'task-23': 0, 'task-26': 0, 'task-8': 0, 'task-0': 0, 'task-6': 0, 'task-15': 0, 'task-20': 0, 'task-9': 0, 'task-17': 0, 'task-3': 0}
    
    # solver = RecoveryModel(env, acs,timelimit=float("inf"))
    # for t, k_fix in fixed_task_mapping.items():        
    #     i = task_to_idx[t]            
    #     solver.model.addConstr(solver.x.sum(i, "*", k_fix) == 1)        
    
    # solution, tasks = solver.solve()        
    # print(solution.solver_metadata)
    
    # global solver in leaf slow
    fixed_task_mapping={'task-12': 0, 'task-16': 0, 'task-2': 0, 'task-19': 0, 'task-5': 0, 'task-1': 0, 'task-14': 0, 'task-22': 0, 'task-7': 0, 'task-21': 0, 'task-4': 0, 'task-27': 0, 'task-25': 0, 'task-24': 0, 'task-10': 0, 'task-13': 0, 'task-23': 0, 'task-26': 0, 'task-8': 0, 'task-0': 0, 'task-6': 0, 'task-15': 0, 'task-20': 0, 'task-9': 0, 'task-17': 0, 'task-3': 1, 'task-11': 1, 'task-18': 1}
    
    solver = ilp_fixed_solver.ilp_fixed_solver.Solver(arg_parser, env, acs,fixed_task_mapping, float("inf"))    
    solution, tasks = solver.solve()        
    print(solution.solver_metadata)
    