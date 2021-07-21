#! /usr/bin/python3
from common import arg_parser as ap
from common import instance
from typing import List, Tuple, Mapping
import gurobipy as grb
import sys
import time
import itertools


class ILPSolver:    
    def __init__(self):
        self.model = None
        self.solved = False
        self.feasible = False
        self.solving_time = None        
        
    def _init_model(self):
        raise NotImplementedError
    
    def solve(self):            
        t_start=time.time()
        self.model.optimize()
        t_end=time.time()
        
        s_feasible=True if self.model.Status == grb.GRB.OPTIMAL or (
            self.model.Status == grb.GRB.TIME_LIMIT and self.model.SolCount > 0) else False
        
        self.solved = True
        self.feasible = s_feasible   
        self.solving_time = t_end - t_start


class MasterModel(ILPSolver):
    def __init__(self, patterns: List[instance.Pattern], major_frame_length: int, tasks: List[str]):
        self.alpha = None
        self.patterns = patterns
        self.major_frame_length = major_frame_length
        self.tasks = tasks
        self.c0 = None
        self.ct = {}        
        
        self._init_model()
        
    def _init_model(self):
        m = grb.Model("Master Model")
        
        # variables
        alpha = m.addVars(len(self.patterns), vtype=grb.GRB.CONTINUOUS, lb=0, ub=1, name="alpha")
        
        # constraints
        # - major frame length        
        self.c0 = m.addConstr(grb.quicksum(alpha[i] * p.length for i, p in enumerate(self.patterns)) <= self.major_frame_length, name="C:major_frame")
        
        # - patterns cover tasks
        for t in self.tasks:                        
            self.ct[t] = m.addConstr(grb.quicksum(alpha[i] for i, p in enumerate(self.patterns) if t in p.task_mapping) >= 1, 
                                                  name="C:task_cover_{}".format(t))  # TODO: should be >= 1 or == 1 ? 
        
        # objective
        m.setObjective(grb.quicksum(alpha[i] * p.cost for i, p in enumerate(self.patterns)), sense=grb.GRB.MINIMIZE)
        
        self.model = m
        self.alpha = alpha
        
    def is_solution_integer(self) -> bool:
        EPS = 1e-4
        for i in range(len(self.alpha)):
            if EPS < self.alpha[i].X < 1 - EPS:
                return False
        return True        
    
    def get_objective(self) -> float:
        if self.feasible:
            return self.model.objVal * (1/self.major_frame_length)
        else:
            return None

                     
    def get_dual_prices(self) -> Tuple[float, Mapping[str, float]]:
        if not self.solved:
            print("warning: get_dual_prices cannot be called for unsolved model; call solve() first", file=sys.stderr)
        if not self.feasible:
            print("warning: model is not feasible, dual prices cannot be obtained", file=sys.stderr)
        return self.c0.Pi, {t: self.ct[t].Pi for t in self.tasks}
    
    def get_solution(self):
        sol = []
        for i, p in enumerate(self.patterns):
            if self.alpha[i].X > 0:  # TODO: comparison
                sol.append({"index": i, "value": self.alpha[i].X})
                
        return sol
    
    def get_selected_patterns(self) -> List[instance.Pattern]:        
        EPS = 1e-4
        return [self.patterns[i] for i in range(len(self.alpha)) if self.alpha[i].X > EPS]
    
    def get_solution_and_tasks(self, env: instance.Environment, acs:  List[instance.AssignmentCharacteristic]):                            
        solution=None
        tasks=[]        

        s_feasible=True if self.model.Status == grb.GRB.OPTIMAL or (
            model.Status == grb.GRB.TIME_LIMIT and model.SolCount > 0) else False
        s_solver_name="BAP"
        s_solution_time=int(round(self.solving_time*1000))  # to ms
        s_windows=[]
        s_metadata={"objective": "-1"}

        if s_feasible:
            s_metadata["objective"] = str(self.model.ObjVal)                                    
            
            for j, p in enumerate(self.patterns):
                if self.alpha[j].X > 0:  # TODO: comparison
                    window_length = p.length
                    window_tasks_assignments=[]
                    
                    if window_length < 1:
                        continue
                                                    
                    # processor-unit allocation (start with all processors empty)
                    pu_allocations={p.name: 0 for p in env.processors_list}
                                    
                    for t in p.task_mapping:
                        ac = [a for a in acs if a.task == t][0]  # assignment characteristic of the current task
                        cur_ra = ac.resource_assignmnets[p.task_mapping[t]]
                        task_processors = []
                        for pr in cur_ra.processors:  
                            window_tasks_assignments.append(instance.TaskAssignment(task=t,
                                                                                    processor=pr.processor,
                                                                                    processing_unit=pu_allocations[pr.processor],
                                                                                    start=0,
                                                                                    length=cur_ra.length))
                            
                                                        
                            # increment the processor units
                            pu_allocations[pr.processor] += pr.processing_units                                
                            task_processors.append(instance.ProcessorAssignment(pr.processor, pr.processing_units))                                 
                                    
                        tasks.append(instance.Task(name=t,
                                                command=ac.command,
                                                length=cur_ra.length,
                                                assignment_index=p.task_mapping[t],
                                                processors=task_processors))                    
                
                    s_windows.append(instance.Window(window_length, window_tasks_assignments))
        else:  # infeasible solution            
            s_feasible=False
            if self.arg_parser.is_arg_present("--iis-output"):
                model.computeIIS()
                model.write(self.arg_parser.get_arg_value("--iis-output") + ".ilp")        
        solution = instance.Solution(s_feasible, s_solver_name, s_solution_time, s_metadata, s_windows)
        
        return (solution, tasks)

        


def get_pair(selected_patterns: List[instance.Pattern], on_same: List[Tuple[str,str]], on_diff: List[Tuple[str,str]]) -> Tuple[str,str]:
    def pair_selection_heuristis(lst: List[Tuple[str,str]]) -> Tuple[str,str]:
        lst = sorted(lst, key=lambda x: task_counter[x[0]] + task_counter[x[1]], reverse=False)
        
        return lst[0]  # TODO: implement some heuristic
        #return lst[random.randint(0,len(lst))]
    
    all_tasks = set()
    for p in selected_patterns:
        all_tasks.update(p.task_mapping.keys())
    
    task_counter = {t: 0 for t in all_tasks}
    for a,b in on_same:
        task_counter[a] += 1
        task_counter[b] += 1
    for a,b in on_diff:
        task_counter[a] += 1
        task_counter[b] += 1
        
    task_to_idx = {t: i for i, t in enumerate(all_tasks)}        
    uf = UnionFind(len(all_tasks))
    
    for a,b in on_same:
        uf.union(task_to_idx[a], task_to_idx[b])        
            
    all_pairs = itertools.combinations(all_tasks, 2)  # combine the tasks
    all_pairs = [p for p in all_pairs if p not in on_same and p not in on_diff]  # filter already used tasks
    all_pairs = [p for p in all_pairs if not uf.find(task_to_idx[p[0]], task_to_idx[p[1]])]  # filter on same components
    
    if all_pairs:
        return pair_selection_heuristis(all_pairs)
    else:
        return None

 
class SubproblemModelILP(ILPSolver):
    
    def __init__(self, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], dual_prices: Tuple[float, Mapping[str, float]],
                 on_same: List[Tuple[str,str]], on_diff: List[Tuple[str,str]]):
        self.env = env
        self.acs = acs
        self.dual_prices = dual_prices 
        self.on_same = on_same
        self.on_diff = on_diff
        self.x_ik = None       
        self.l = None        
        
        self._init_model()        
        
    def _init_model(self):
        m = grb.Model("Subproblem-ILP")
        num_tasks = len(self.acs)
        
        task_to_idx = {}
        for i, a in enumerate(self.acs):
            task_to_idx[a.task] = i

        # variables
        x_ik = m.addVars([(i, k)
                          for i in range(num_tasks)                               
                          for k in range(len(self.acs[i].resource_assignmnets))],
                          vtype=grb.GRB.BINARY,
                          name="x")        
        l = m.addVar(vtype=grb.GRB.INTEGER, lb=0, name="l")
        B = m.addVar(vtype=grb.GRB.CONTINUOUS, lb=0, name="B")                    
        
        # constraints
        # - B value
        M = self.env.major_frame_length * max([self.acs[i].resource_assignmnets[k].intercept
                                                for i in range(num_tasks)
                                                for k in range(len(self.acs[i].resource_assignmnets))])
        m.addConstrs(B >= l * self.acs[i].resource_assignmnets[k].intercept - M * (1-x_ik[i,k])
                     for i in range(num_tasks)
                     for k in range(len(self.acs[i].resource_assignmnets)))
        
        # - assign task to at most one resource
        m.addConstrs(x_ik.sum(i, "*") <= 1
                    for i in range(num_tasks))
        
        # - respect capacity of the resource        
        m.addConstrs((grb.quicksum(x_ik[i, k] * acp.processing_units
                                       for i in range(num_tasks)
                                       for k in range(len(self.acs[i].resource_assignmnets))
                                       for acp in self.acs[i].resource_assignmnets[k].processors if acp.processor == processor.name)
                          <= processor.processing_units
                          for processor in self.env.processors_list),
                         name="resource capacity")
        
        # - constrain window length
        m.addConstrs(l >= x_ik[i, k] * self.acs[i].resource_assignmnets[k].length
                     for i in range(num_tasks)
                     for k in range(len(self.acs[i].resource_assignmnets)))
        m.addConstr(l <= self.env.major_frame_length)

        # - branching constraints
        for t1, t2 in self.on_same:
            i1 = task_to_idx[t1]
            i2 = task_to_idx[t2]
            m.addConstr(x_ik.sum(i1, "*") == x_ik.sum(i2,"*"))  # in same window

        for t1, t2 in self.on_diff:
            i1 = task_to_idx[t1]
            i2 = task_to_idx[t2]
            m.addConstr(x_ik.sum(i1, "*") + x_ik.sum(i2,"*") <= 1)  # in different windows
        
        # objective
        obj = grb.quicksum(x_ik[i, k] * (self.acs[i].resource_assignmnets[k].length
                                         * self.acs[i].resource_assignmnets[k].slope 
                                         -  self.dual_prices[1][self.acs[i].task])
                           for i in range(num_tasks)
                           for k in range(len(self.acs[i].resource_assignmnets))) - l*self.dual_prices[0] + B      
        m.setObjective(obj, sense=grb.GRB.MINIMIZE)
        
        self.model = m
        self.x_ik = x_ik
        self.l = l
        
    def get_pattern(self) -> instance.Pattern:
        if not self.solved:
            print("warning: the model was not solved", f=sys.stderr)
            return None
        if not self.feasible:
            print("warning: the model is not feasible", f=sys.stderr)
            return None
        
        p_len = int(round(self.l.X))
        #p_cost = self.model.ObjVal + self.dual_prices[0] * p_len        
        p_task_mapping = {}
        
        for i in range(len(self.acs)):
            for k in range(len(self.acs[i].resource_assignmnets)):
                if self.x_ik[i,k].X > 0.5:
                    p_task_mapping[self.acs[i].task] = k
                    #p_cost += self.dual_prices[1][self.acs[i].task]
                    break

        # recompute the cost manually to avoid potential numerical problems
        pattern = instance.Pattern(0, p_len, p_task_mapping)                
        cost = pattern.compute_cost(self.acs)
        pattern.cost = cost
        
        return pattern
   
    def get_patterns(self) -> List[instance.Pattern]:
        if not self.solved:
            print("warning: the model was not solved", f=sys.stderr)
            return None
        if not self.feasible:
            print("warning: the model is not feasible", f=sys.stderr)
            return None
        
        patterns = []
        
        for sol_idx in range(self.model.SolCount):
            self.model.setParam("SolutionNumber", sol_idx)
            
            if self.model.PoolObjVal < -0.0001:  # TODO: some robust check
        
                p_len = int(round(self.l.Xn))            
                p_task_mapping = {}
            
                for i in range(len(self.acs)):
                    for k in range(len(self.acs[i].resource_assignmnets)):
                        if self.x_ik[i,k].Xn > 0.5:
                            p_task_mapping[self.acs[i].task] = k                        
                            break

                # recompute the cost manually to avoid potential numerical problems
                pattern = instance.Pattern(0, p_len, p_task_mapping)                
                cost = pattern.compute_cost(self.acs)
                pattern.cost = cost

                patterns.append(pattern)
                        
        return patterns    
        
class RecoveryModel(ILPSolver):
    def __init__(self, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], 
                 on_same: List[Tuple[str,str]], on_diff: List[Tuple[str,str]]):
        self.env = env
        self.acs = acs 
        self.on_same = on_same
        self.on_diff = on_diff
        self.x = None
        self.l = None
        
        self._init_model()
        
    def _init_model(self):
        task_to_idx = {}
        for i, a in enumerate(self.acs):
            task_to_idx[a.task] = i
        num_tasks = len(self.acs)
            
        m = grb.Model("RecoveryModel")                
        
        # variables
        x_ijk = m.addVars([(i, j, k)
                           for i in range(num_tasks)
                           for j in range(num_tasks)
                           for k in range(len(self.acs[i].resource_assignmnets))],
                          vtype=grb.GRB.BINARY,
                          name="x")               
        l_j = m.addVars(num_tasks, vtype=grb.GRB.INTEGER, lb=0, name="l")
        
        # constraints
        # - each task is in some window
        m.addConstrs(x_ijk.sum(i, "*", "*") == 1 for i in range(num_tasks))
        
        # - resource capacities are held                        
        m.addConstrs((grb.quicksum(x_ijk[i,j, k] * acp.processing_units
                                   for i in range(num_tasks)
                                   for k in range(len(self.acs[i].resource_assignmnets))
                                   for acp in self.acs[i].resource_assignmnets[k].processors if acp.processor == processor.name)
                      <= processor.processing_units
                      for processor in self.env.processors_list
                      for j in range(num_tasks)),
                      name="resource capacity")
        
        # - constrain window length
        m.addConstrs(l_j[j] >= x_ijk[i, j, k] * self.acs[i].resource_assignmnets[k].length
                     for i in range(num_tasks)
                     for j in range(num_tasks)
                     for k in range(len(self.acs[i].resource_assignmnets)))

        # - major frame length
        m.addConstr(l_j.sum("*") <= self.env.major_frame_length)
        
        # - branching constraints
        for t1, t2 in self.on_same:
            i1 = task_to_idx[t1]
            i2 = task_to_idx[t2]
            m.addConstrs(x_ijk.sum(i1, j, "*") == x_ijk.sum(i2, j, "*") for j in range(num_tasks))  # in same window

        for t1, t2 in self.on_diff:
            i1 = task_to_idx[t1]
            i2 = task_to_idx[t2]
            m.addConstrs(x_ijk.sum(i1, j, "*") + x_ijk.sum(i2, j, "*") <= 1 for j in range(num_tasks))  # in different windows
                        
        # objective
        # either none (just check feasibility) or minimize the total length
        
        self.model = m
        self.x = x_ijk
        self.l = l_j
        
    def get_patterns(self) -> List[instance.Pattern]:
        num_tasks = len(self.acs)
        patterns = []
        
        if self.solved and self.feasible:            
            for j in range(num_tasks):
                task_mapping = {}
                length = 0
                
                for i in range(num_tasks):
                    for k in range(len(self.acs[i].resource_assignmnets)):
                        if self.x[i,j,k].X > 0.5:
                            task_mapping[self.acs[i].task] = k
                            length = max(length, self.acs[i].resource_assignmnets[k].length)
                
                if task_mapping:
                    pattern = instance.Pattern(-1, length, task_mapping) 
                    pattern.cost = pattern.compute_cost(self.acs)
                    patterns.append(pattern)
                            
        return patterns
         
       
class BranchAndPriceSolver:

    def __init__(self, arg_parser: ap.ArgParser, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], init_data_path: str):
        self.arg_parser = arg_parser
        self.env = env
        self.acs = acs
        self.init_data_path = init_data_path
        self.patterns = None
        
        self.number_of_nodes = 0
        self.best_objective = float('inf')
        self.best_solution = None
        self.solving_time = None
        

    def solve(self) -> Tuple[instance.Solution, List[instance.Task]]:        
        if self.init_data_path:  # initialize from data file
            json_data = instance.read_json_from_file(self.init_data_path)
                        
            patterns = instance.get_patterns(json_data)
            self.best_objective = instance.get_solution_objective(json_data)        
        else:  # use Recovery model for initialization
            print("warning: the method has not been initialized.", file=sys.stderr)
            print("info: trying the RecoveryModel")
            
            rm = RecoveryModel(self.env, self.acs, [], [])
            rm.solve()            
            patterns = rm.get_patterns()
            self.best_objective = sum([p.cost for p in patterns])                                    
        
        if patterns:        
            t_start=time.time()    
            sol = self.branch_and_price([], [], patterns)
            t_end=time.time()

            self.solving_time = int((t_end - t_start) * 1000)  # to ms
        
            print("info: search ended")
            if sol:
                print("info: solution quality {:f}".format(self.best_objective))
            else:
                sol = instance.Solution(False, "BAP", self.solving_time, {}, []), []                                            
                # TODO - initial solution is the best, reconstruct it 
                # TODO : is it necessary? can this branch be reached?
                #rm_patterns = rm.get_patterns()                
                # solution = instance.Solution(True, "BAP", self.solving_time, {"objective": self.best_objective}, [p.to_window() for p in rm_patterns])  # TODO: rm.get_patterns not necessart
                # tasks = []
                
                # for p in rm_patterns:
                #     for t in p.task_mapping:
                #         for a in self.acs:
                #             if t != a.task:
                #                 continue
                #             else:                                
                #                 task_processors = []                                    
                #                 for p in ac.processors:
                #                     task_processors.append(instance.ProcessorAssignment(p.processor, p.processing_units))
                                
                #                 tasks.append(instance.Task(name=t,
                #                                            command=a.command,
                #                                             length=a[p.task_mapping[t]].length,
                #                                             assignment_index=p.task_mapping[t],
                #                                             processors=task_processors))                    
        
                


        else:
            print("warning: no patterns were provided or recovery model could not find any solution", file=sys.stderr)
            self.solving_time = 0           
            sol = instance.Solution(False, "BAP", self.solving_time, {}, []), []            
        
        return sol

    def branch_and_price(self, on_same: List[Tuple[str,str]], on_diff: List[Tuple[str,str]], patterns: List[instance.Pattern]):
        env = self.env 
        acs = self.acs      
        tasks = [ac.task for ac in acs]
        print("info: branching, on same = {:s}, on diff = {:s}".format(str(on_same), str(on_diff)))    
        
        print("PATTERNS")
        for p in patterns:
            print("    ", p.to_dict())

        # Iterate - master -> subproblem
        while True:            
            # - solve restricted master problem
            mm = MasterModel(patterns, env.major_frame_length, tasks)
            mm.solve()
            
            if not mm.feasible:
                print("warning: master model is not feasible.", file=sys.stderr)
                return None
            
            pi0, pit = mm.get_dual_prices()
                
            # - solve subproblem
            ss = SubproblemModelILP(env, acs, (pi0, pit), on_same, on_diff)
            ss.solve()
            
            if not ss.feasible:
                print("warning: subproblem model is not feasible.", file=sys.stderr)
                return None
                        
            EPS = 1e-4
            if ss.model.ObjVal >= -EPS:  # no more improving patterns exist
                print("info: subproblem objective was non-negative; ending the iteration.")
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
                print("  info: found pattern", p.to_dict())
                patterns.append(p)                                              
        # END of pattern generation phase ----------------------------------------------------------------------------------

        # Solve master model to get the optimal solution of the relaxed problem
        # - solve restricted master problem
        mm = MasterModel(patterns, env.major_frame_length, [ac.task for ac in acs])
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
        EPS = 1e-4
        if mm.get_objective() > self.best_objective + EPS:  # Check if master model is worse than best so far solution
            print("info: master model solution ({:f}) is worse than best-so-far solution ({:f}).".format(mm.get_objective(), self.best_objective))
            return None

        if mm.is_solution_integer():  # Check if solution is integer            
            EPS = 1e-4            
            if mm.get_objective() < self.best_objective + EPS:
                self.best_objective = mm.get_objective()
                print("info: best objective was updated to:", self.best_objective)            
                                    
            return mm.get_solution_and_tasks(self.env, self.acs)
        else:
            print("info: master model solution is not integer.")

            # Create two branches and return better solution
            pair = get_pair(mm.get_selected_patterns(), on_same, on_diff)        
            
            if pair is None:  # There was no pair to generate
                print("warning: there is no pair to generate for branching.", file=sys.stderr)
                return None
            else:
                print("info: branching on pair", pair)

            # Generate new lists
            on_same_new = on_same.copy()
            on_diff_new = on_diff.copy()
            on_diff_new.append(pair)
            on_same_new.append(pair)                                                     
            
            p_same = [p for p in patterns if ((pair[0] in p.task_mapping and pair[1] in p.task_mapping)
                                            or (pair[0] not in p.task_mapping and pair[1] not in p.task_mapping))]
            p_diff = [p for p in patterns if not (pair[0] in p.task_mapping and pair[1] in p.task_mapping)]

            # - two branches
            # - on same
            rm = RecoveryModel(self.env, self.acs, on_same_new, on_diff)
            rm.solve()
            if rm.feasible:
                for p in rm.get_patterns():
                    if p.task_mapping not in [x.task_mapping for x in p_same]:
                        p_same.append(p)                
                sol_same = self.branch_and_price(on_same_new, on_diff, p_same)
            else:
                print("info: RecoveryModel was not feasible (on_same)")
                sol_same = None
                
            # - on diff
            rm = RecoveryModel(self.env, self.acs, on_same, on_diff_new)
            rm.solve()
            if rm.feasible:
                for p in rm.get_patterns():
                    if p.task_mapping not in [x.task_mapping for x in p_diff]:
                        p_diff.append(p)                                
                sol_diff = self.branch_and_price(on_same, on_diff_new, p_diff)
            else:
                print("info: RecoveryModel was not feasible (on_diff)")
                sol_diff = None

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
