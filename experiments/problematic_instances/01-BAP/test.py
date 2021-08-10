#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/common/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/decomposed_solver/'))
sys.path.append(os.path.join(os.path.dirname(__file__), './../../../tools/src/'))

import instance
from decomposed_solver import *
import numpy as np 

if __name__ == "__main__":
    json_data = instance.read_json_from_file("IN_047.json")
    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)    
    tasks = [ac.task for ac in acs]

on_same = []
on_diff = []

patterns = [
    instance.Pattern(1.109577745287508, 1, {'task-6': 1}),
    instance.Pattern(50.60591074013507, 30, {'task-4': 0, 'task-8': 1}),
    instance.Pattern(6.995009545769157, 14, {'task-5': 0}),
    instance.Pattern(9.884697924002534, 10, {'task-2': 0, 'task-7': 1}),
    instance.Pattern(53.714988389112726, 36, {'task-3': 0, 'task-9': 1}),
    instance.Pattern(77.88835842811017, 42, {'task-0': 1, 'task-1': 1}),
    instance.Pattern(73.2053952153213, 42, {'task-0': 1, 'task-8': 0, 'task-9': 1}),
    instance.Pattern(81.22294449958616, 42, {'task-0': 1, 'task-4': 0}),
    instance.Pattern(22.99167035525402, 23, {'task-1': 1, 'task-4': 0}),
    instance.Pattern(112.6918784318598, 42, {'task-0': 1, 'task-1': 1, 'task-3': 0})
    #instance.Pattern(47.4683662468998, 36, {'task-3': 0})
]

last_prices = None

for ii in range(3):
    mm = MasterModel(patterns, env.major_frame_length, tasks)
    mm.model.setParam("OutputFlag", 0)
    mm.model.setParam("Presolve", 0)  # When presolve is turned on -> one pattern is generated multiple times
    mm.solve()
    #mm.model.write("mm_{:d}.sol".format(ii))
    #mm.model.write("mm_{:d}.lp".format(ii))

    if not mm.feasible:
        print("master not feasible")

    pi0, pit = mm.get_dual_prices()
    #print("dual prices", pi0)
    #for x in pit:
    #    print(x, pit[x])    
        
    if last_prices is not None:
        print("diff in last two dual prices", np.sum(last_prices - np.array([pit[x] for x in pit])))
    last_prices = np.array([pit[x] for x in pit])

    ss = SubproblemModelILP(env, acs, (pi0, pit))
    ss.model.setParam("OutputFlag", 0)
    ss.solve()
    #ss.model.write("ss_{:d}.sol".format(ii))
    #ss.model.write("ss_{:d}.lp".format(ii))

    if not ss.feasible:
        print("subproblem not feasible")
                
    EPS = 1e-4
    if ss.model.ObjVal >= -EPS:  # no more improving patterns exist
        print("subproblem non negative")
    else:
        p = ss.get_pattern()
        print("  found pattern {:s}, {:s}".format(str(p.to_dict()), str(ss.model.ObjVal)))
        patterns.append(p)      

