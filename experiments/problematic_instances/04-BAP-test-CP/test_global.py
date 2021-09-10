#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/common/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/ilp_global_solver/'))


import instance
import arg_parser
from ilp_global_solver import Solver, SolverFixed
import numpy as np 
import time
import docplex.cp.modeler as cpmod
import numpy.random as rnd

if __name__ == "__main__":    
    rnd.seed(13) #rnd.seed(17)
    ap = arg_parser.ArgParser()
    
    #json_data = instance.read_json_from_file("IN_015.json")
    json_data = instance.read_json_from_file("IN_001.json")
    
    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)    
    tasks = [ac.task for ac in acs]
    task_to_idx = {t: i for i, t in enumerate(tasks)} 
                
    # Fixed solver (leaf)
    print("New")
    solver = SolverFixed(ap, env, acs, timelimit=5)
    sol, tasks = solver.solve()
    print("time", sol.solution_time)
    tasks = sorted(tasks, key=lambda x: x.name)
    for m in sol.solver_metadata:
        print(m, sol.solver_metadata[m])    
    # for t in tasks:
    #     print(t.to_dict())
    for w in sol.windows:
        print(w.to_dict())
    
    # Fixed solver (leaf)
    print("Original")
    solver = Solver(ap, env, acs, timelimit=5)
    sol, tasks = solver.solve()
    tasks = sorted(tasks, key=lambda x: x.name)
    print("time", sol.solution_time)
    for m in sol.solver_metadata:
        print(m, sol.solver_metadata[m])    
    # for t in tasks:
    #     print(t.to_dict())
    for w in sol.windows:
        print(w.to_dict())        
    