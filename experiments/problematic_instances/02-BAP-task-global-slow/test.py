#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/common/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/decomposed_solver/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/ilp_global_solver/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/ilp_fixed_solver/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/'))

import instance
import arg_parser
from ilp_global_solver import Solver
import ilp_fixed_solver
import numpy as np 

if __name__ == "__main__":    
    ap = arg_parser.ArgParser()
    json_data = instance.read_json_from_file("IN_079.json")
    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)    
    tasks = [ac.task for ac in acs]
    task_to_idx = {t: i for i, t in enumerate(tasks)} 
    
    # Try global solver
    solver = Solver(ap, env, acs, timelimit=float("inf"))
    solution, tasks = solver.solve()  
          
    print(solution.solver_metadata)

    # Try with fixed assignment:
    fixed_task_mapping={'task-2': 0, 'task-12': 1, 'task-3': 0, 'task-5': 1, 'task-1': 1, 'task-11': 1, 'task-0': 1, 'task-6': 0, 'task-10': 0, 'task-9': 0, 'task-14': 0, 'task-7': 1, 'task-8': 1, 'task-13': 0, 'task-4': 1}    
    solver = Solver(ap, env, acs, timelimit=float("inf"))
    for t, k_fix in fixed_task_mapping.items():
        i = task_to_idx[t]            
        solver.model.addConstr(solver.x_ijk.sum(i, "*", k_fix) == 1)        
    
    solution, tasks = solver.solve()        
    print(solution.solver_metadata)
    
    # Try fixed solver
    s = ilp_fixed_solver.Solver(ap, env, acs, fixed_task_mapping, timelimit=float("inf"))
    solution, tasks = s.solve()  
    print(solution.solver_metadata)
    

