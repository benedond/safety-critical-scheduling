#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common import instance
from common import arg_parser
import decomposed_solver
import json
from typing import List, Tuple, Mapping

# python tools/src/decomposed_solver/main.py --input ./experiments/test_decomposition/IN_20.json 



def branch_and_price(env: instance.Environment,
                     acs: List[instance.AssignmentCharacteristic],
                     on_same: List[Tuple[str,str]],
                     on_diff: List[Tuple[str,str]],
                     patterns: List[instance.Pattern]):
            
    print("info: branching, on same = {:s}, on diff = {:s}".format(str(on_same), str(on_diff)))    

    # Iterate - master -> subproblem
    while True:
            
        # - solve restricted master problem
        mm = decomposed_solver.MasterModel(patterns, env.major_frame_length, [ac.task for ac in acs])
        mm.solve()
        
        if not mm.feasible:
            print("warning: master model is not feasible.", file=sys.stderr)
            return None
        
        pi0, pit = mm.get_dual_prices()
        
        # print(pi0)
        # for k in pit:
        #     print("{:22s} -> {:f}".format(k,pit[k]))
            
        # - solve subproblem
        ss = decomposed_solver.SubproblemModelILP(env, acs, (pi0, pit))
        ss.solve()
        
        if not ss.feasible:
            print("warning: subproblem model is not feasible.", file=sys.stderr)
            return None
        
        if ss.model.ObjVal >= 0:  # no more improving patterns exist
            break
            # for s in mm.get_solution():
            #     print(s)       
            # mm.model.write("MP.sol")     
            # mm.model.write("MP.lp") 
            
            # for i, p in enumerate(patterns):
            #     print(i, p.to_dict())  
            #     # p.check_cost(acs)      
            #     # p.check_length(acs)                                      
        else:
            p = ss.get_pattern()
            print("info: found pattern", p.to_dict())
            patterns.append(p)                                              
    # END of pattern generation phase ----------------------------------------------------------------------------------

    # Solve master model to get the optimal solution of the relaxed problem
    # - solve restricted master problem
    mm = decomposed_solver.MasterModel(patterns, env.major_frame_length, [ac.task for ac in acs])
    mm.solve()
    

    if not mm.solved:
        print("warning: master model was not solved.", file=sys.stderr)
        return None

    # BRANCHING
    if not mm.feasible:
        print("warning: master model was not feasible.", file=sys.stderr)            
        return None

    # if master_model.alpha_is_not_zero():  # If alpha > 0 - there is no solution to relaxed master model without alpha
    #     if params.PRINT_BB:
    #         print("[B&P:] Master model - alpha is not zero: alpha =", master_model.alpha.X)
    #     return None

    if mm.model.objVal > glob_best_obj:  # Check if master model is worse than best so far solution
        print("info: master model solution is worst than best-so-far solution.")            
        return None

    if mm.is_solution_integer():  # Check if solution is integer
        master_solution = get_solution(master_model, p_wrap)
        
        # TODO: update best so far
        # if master_model.model.objVal < glob_best_obj:
        #     glob_best_obj = master_model.model.objVal
        
        # TODO: get master solution        
        return mm.get_solution
    else:
        print("info: master model solution is not integer.")

        # Create two branches and return better solution
        pair = decomposed_solver.get_pair(mm.get_selected_patterns(), on_same, on_diff)        
        
        if pair is None:  # There was no pair to generate
            return None

        # Generate new lists
        on_same_new = on_same.copy()
        on_diff_new = on_diff.copy()
        on_diff_new.append(pair)
        on_same_new.append(pair)

        p_wrap_same, p_wrap_diff = generate_new_patterns(p_wrap, pair)
        
        p_same = [p for p in patterns if ((pair[0] in p.task_mapping and p[1] in p.task_mapping)
                                          or (pair[0] not in p.task_mapping and p[1] not in p.task_mapping))]
        p_diff = [p for p in patterns if not (pair[0] in p.task_mapping and pair[1] in p.task_mapping)]

        # - two branches
        sol_same = branch_and_price(instance, on_same_new, on_diff, p_same)
        sol_diff = branch_and_price(instance, on_same, on_diff_new, p_diff)

        return get_better_sol(sol_same, sol_diff)

def get_better_sol(sol1: Tuple[instance.Solution, List[instance.Task]], sol2: Tuple[instance.Solution, List[instance.Task]]) -> Tuple[instance.Solution, List[instance.Task]]:    
    if sol1 is None and sol2 is None:
        return None
    elif sol1 is None and sol2 is not None:
        return sol2
    elif sol1 is not None and sol2 is None:
        return sol1
    else:
        if sol1[0].solver_metadata["objective"] < sol2[0].solver_metadata["objective"]:
            return sol1
        else:
            return sol2


if __name__ == "__main__":

    ap = arg_parser.ArgParser()
    input_filename = ap.get_arg_value("--input")

    if input_filename:
        json_data = instance.read_json_from_file(input_filename)
    else:
        json_data = json.load(sys.stdin)
    
    env = instance.parse_environment(json_data)
    acs = instance.parse_assignment_characteristics(json_data)    

    init_data = instance.read_json_from_file("/home/benedond/Doktorat/Vyzkum/Projects/safety-critical-scheduling/experiments/test_decomposition/IN_20_solution.json")
    patterns = instance.get_patterns(init_data)
    for p in patterns:
        print(p.to_dict())        
    
    sol = branch_and_price(env, acs, [], [], patterns)
    
