#! /usr/bin/python3
from common import arg_parser as ap
from common import instance
from typing import List, Tuple, Mapping
from ilp_global_solver import ilp_global_solver
import gurobipy as grb
import sys
import time
import itertools
from numpy import random
import logging
from common.union_find import UnionFind


class ILPSolver:    
    def __init__(self):
        self.model = None
        self.solved = False
        self.feasible = False
        self.solving_time = None
        self.init_time = None  
        
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

    def time_limit_reached(self):
        return self.model.Status == grb.GRB.TIME_LIMIT


class MasterModel(ILPSolver):
    def __init__(self, patterns: List[instance.Pattern], major_frame_length: int, tasks: List[str], bin_vars: bool=False, timelimit: float=float("inf")):
        self.alpha = None
        self.patterns = patterns
        self.major_frame_length = major_frame_length
        self.tasks = tasks
        self.c0 = None
        self.ct = {}        
        self.bin_vars = bin_vars
        self.timelimit = timelimit
        
        t_s = time.time()
        self._init_model()
        t_e = time.time()
        self.init_time = t_e - t_s
        
    def _init_model(self):
        m = grb.Model("Master Model")
        m.setParam("TimeLimit", self.timelimit)
        
        # variables
        if self.bin_vars:
            alpha = m.addVars(len(self.patterns), vtype=grb.GRB.BINARY, lb=0, ub=1, name="alpha")
        else:
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
            logging.warning("get_dual_prices cannot be called for unsolved model; call solve() first")            
        if not self.feasible:
            logging.warning("model is not feasible, dual prices cannot be obtained")
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
            s_metadata["objective"] = str(self.model.ObjVal / self.major_frame_length) 
            
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
        
    used_by_on_diff = set()
    for i,j in on_diff:
        used_by_on_diff.add((uf._root(task_to_idx[i]), uf._root(task_to_idx[j])))  
        used_by_on_diff.add((uf._root(task_to_idx[j]), uf._root(task_to_idx[i])))  
            
    all_pairs = itertools.combinations(all_tasks, 2)  # combine the tasks
    all_pairs = [p for p in all_pairs if p not in on_same and p not in on_diff]  # filter already used tasks
    all_pairs = [p for p in all_pairs if not uf.find(task_to_idx[p[0]], task_to_idx[p[1]])]  # filter on same components
    all_pairs = [p for p in all_pairs if (uf._root(task_to_idx[p[0]]), uf._root(task_to_idx[p[1]])) not in used_by_on_diff]  # filter on diff components
    
    if all_pairs:
        return pair_selection_heuristis(all_pairs)
    else:
        return None

 
class SubproblemModelILP(ILPSolver):
    
    def __init__(self, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], dual_prices: Tuple[float, Mapping[str, float]],
                 on_same: List[Tuple[str,str]], on_diff: List[Tuple[str,str]], timelimit: float=float("inf")):
        self.env = env
        self.acs = acs
        self.dual_prices = dual_prices 
        self.on_same = on_same
        self.on_diff = on_diff
        self.x_ik = None       
        self.l = None        
        self.timelimit = timelimit
        
        t_s = time.time()
        self._init_model()        
        t_e = time.time()
        self.init_time = t_e - t_s
        
    def _init_model(self):
        m = grb.Model("Subproblem-ILP")
        m.setParam("TimeLimit", self.timelimit)
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
            #m.addConstr(x_ik[i1, k] == x_ik[i2, k] for k in range(len(self.acs[i].resource_assignmnets)))  # in same window

        for t1, t2 in self.on_diff:
            i1 = task_to_idx[t1]
            i2 = task_to_idx[t2]
            m.addConstr(x_ik.sum(i1, "*") + x_ik.sum(i2,"*") <= 1 )  # in different windows
            #m.addConstr(x_ik[i1, k] + x_ik[i2,k] <= 1 for k in range(len(self.acs[i].resource_assignmnets)))  # in different windows
        
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
            logging.warning("model was not solved")
            return None
        if not self.feasible:
            logging.warning("model is not feasible")
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
            logging.warning("model was not solved")
            return None
        if not self.feasible:
            logging.warning("model is not feasible")
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
                 on_same: List[Tuple[str,str]], on_diff: List[Tuple[str,str]], timelimit: float=float("inf")):
        self.env = env
        self.acs = acs 
        self.on_same = on_same
        self.on_diff = on_diff
        self.x = None
        self.l = None
        self.timelimit = timelimit
        
        t_s = time.time()
        self._init_model()
        t_e = time.time()
        self.init_time = t_e - t_s
        
    def _init_model(self):
        task_to_idx = {}
        for i, a in enumerate(self.acs):
            task_to_idx[a.task] = i
        num_tasks = len(self.acs)
            
        m = grb.Model("RecoveryModel")                
        m.setParam("TimeLimit", self.timelimit)            
        
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
            # m.addConstrs(x_ijk[i1, j, k] == x_ijk[i2, j, k] for j in range(num_tasks) for k in range(len(self.acs[i].resource_assignmnets)))

        for t1, t2 in self.on_diff:
            i1 = task_to_idx[t1]
            i2 = task_to_idx[t2]
            m.addConstrs(x_ijk.sum(i1, j, "*") + x_ijk.sum(i2, j, "*") <= 1 for j in range(num_tasks))  # in different windows
            # m.addConstrs(x_ijk[i1, j, k] + x_ijk[i2, j, k] <= 1 for j in range(num_tasks) for k in range(len(self.acs[i].resource_assignmnets)))
                        
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

    def __init__(self, arg_parser: ap.ArgParser, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], init_data_path: str, timelimit: float=float("inf")):
        self.arg_parser = arg_parser
        self.env = env
        self.acs = acs
        self.task_to_ac = instance.get_task_to_acs_map(self.acs)
        self.init_data_path = init_data_path
        self.patterns = None
        self.timelimit = timelimit
        self.time_start = None
                
        self.best_objective = float('inf')        
        self.solving_time = 0
        
        # statistics
        self.number_of_nodes = 0
        self.time_masters_init = 0
        self.time_masters_solving = 0
        self.time_sub_init = 0
        self.time_sub_solving = 0
        self.time_global_solving = 0
        self.time_get_pair = 0
        self.time_recovery = 0
        self.master_relaxation = -1
        self.interrupted = False  # might be due to timelimit or same pattern generation, etc.
        self.patterns_generated_num = []  # number of generated patterns in each node 
        
    def _get_remaining_time(self):
        return max(0, self.timelimit - (time.time() - self.time_start))

    def solve(self) -> Tuple[instance.Solution, List[instance.Task]]:        
        t_s = time.time()
        self.time_start = t_s
        # INITIAL SOLUTION
        if self.init_data_path:  # initialize from data file
            json_data = instance.read_json_from_file(self.init_data_path)
            
                        
            patterns = instance.get_patterns(json_data)
            self.best_objective = instance.get_solution_objective(json_data)        
        else:  # use Recovery model for initialization            
            logging.info("no init data provided, trying the RecoveryModel")            
            rm = RecoveryModel(self.env, self.acs, [], [], timelimit=self._get_remaining_time())
            rm.solve()
            patterns = rm.get_patterns()
            self.best_objective = sum([p.cost for p in patterns]) / self.env.major_frame_length
            self.time_recovery += rm.solving_time + rm.init_time
                        
        # BRANCH AND PRICE
        if patterns:
            logging.info("initial objective {:f}".format(self.best_objective))
            sol = instance.Solution(True, "BAP", self.solving_time,
                                         {"objective": str(self.best_objective)}, 
                                         [p.to_window(self.env, self.task_to_ac) for p in patterns])
            tasks = instance.patterns_to_task(patterns, self.task_to_ac)
            
            # Start beanch-and-price
            t_start=time.time()    
            bab_s = self.branch_and_price([], [], patterns)
            t_end=time.time()

            self.solving_time = int((t_end - t_start) * 1000)  # to ms
                    
            logging.info("search ended")
            logging.info("solution quality {:f}".format(self.best_objective))
            
            if bab_s:  # use the initial solution if nothing better was found
                sol, tasks = bab_s
        else:        
            logging.info("no initial solution was provided/found")
            sol = instance.Solution(False, "BAP", self.solving_time, {}, [])
            tasks = []
            
        t_e = time.time()
        
        sol.solution_time = int(round((t_e - t_s) * 1000))
        # add metadata
        sol.solver_metadata["number_of_nodes"] = str(self.number_of_nodes)
        sol.solver_metadata["time_masters_init"] = "{:0.2f}".format(self.time_masters_init)
        sol.solver_metadata["time_masters_solving"] = "{:0.2f}".format(self.time_masters_solving)
        sol.solver_metadata["time_sub_init"] = "{:0.2f}".format(self.time_sub_init)
        sol.solver_metadata["time_sub_solving"] = "{:0.2f}".format(self.time_sub_solving)
        sol.solver_metadata["time_global"] = "{:0.2f}".format(self.time_global_solving)
        sol.solver_metadata["time_get_pair"] = "{:0.2f}".format(self.time_get_pair)
        sol.solver_metadata["time_recovery"] = "{:0.2f}".format(self.time_recovery)
        sol.solver_metadata["master_relaxation"] = "{:0.6f}".format(self.master_relaxation)
        if self.patterns_generated_num:
            sol.solver_metadata["patterns_generated_avg"] = "{:0.2f}".format(sum(self.patterns_generated_num) / len(self.patterns_generated_num))                
        else:
            sol.solver_metadata["patterns_generated_avg"] = "0"
        sol.solver_metadata["optimal"] = str(not self.interrupted)
                    
        return sol, tasks

    def branch_and_price(self, on_same: List[Tuple[str,str]], on_diff: List[Tuple[str,str]], patterns: List[instance.Pattern]):
        logging.info("branching, on same = {:s}, on diff = {:s}".format(str(on_same), str(on_diff)))            
        if not self._get_remaining_time():  # reamining time is 0
            logging.warning("timelimit was reached; exiting the branch")
            self.interrupted = True
            return None
        
        env = self.env 
        acs = self.acs      
        tasks = [ac.task for ac in acs]
        logging.info("branching, on same = {:s}, on diff = {:s}".format(str(on_same), str(on_diff)))            
        
        self.number_of_nodes += 1
        
        logging.info("PATTERNS {:d}".format(len(patterns)))
        for p in patterns:
            logging.info("    {:s}".format(str(p.to_dict())))

        # Iterate - master -> subproblem
        n_patterns = 0
        while True:            
            # - solve restricted master problem
            mm = MasterModel(patterns, env.major_frame_length, tasks, timelimit=self._get_remaining_time())            
            mm.solve()
            
            # - stats info (master)
            self.time_masters_init += mm.init_time
            self.time_masters_solving += mm.solving_time
            
            if mm.time_limit_reached():
                logging.warning("master model reached timelimit.")
                self.interrupted = True
                return None
            
            if not mm.feasible:
                logging.warning("master model is not feasible.")
                return None
            
            pi0, pit = mm.get_dual_prices()
                
            # - solve subproblem
            ss = SubproblemModelILP(env, acs, (pi0, pit), on_same, on_diff)
            ss.solve()
            
            if ss.time_limit_reached():
                self.interrupted = True
                return None
            # - stats info (subproblem)
            self.time_sub_init += ss.init_time
            self.time_sub_solving += ss.solving_time 
            
            if not ss.feasible:
                logging.warning("subproblem model is not feasible.")
                return None
                        
            EPS = 1e-3
            if ss.model.ObjVal >= -EPS:  # no more improving patterns exist
                logging.info("subproblem objective was non-negative; ending the iteration.")
                break                                    
            else:
                p = ss.get_pattern()
                logging.info("  found pattern {:s}, {:s}".format(str(p.to_dict()), str(ss.model.ObjVal)))
                patterns.append(p)      
                n_patterns += 1                                        
        # END of pattern generation phase ----------------------------------------------------------------------------------
        
        self.patterns_generated_num.append(n_patterns)

        # Solve master model to get the optimal solution of the relaxed problem
        # - solve restricted master problem
        mm = MasterModel(patterns, env.major_frame_length, [ac.task for ac in acs], timelimit=self._get_remaining_time())
        mm.solve()                       
                
        if mm.time_limit_reached():
            logging.warning("master model reached timelimit.")
            self.interrupted = True
            return None
        # - stats info (master)
        self.time_masters_init += mm.init_time
        self.time_masters_solving += mm.solving_time
        
        if self.number_of_nodes == 1:  # root node
            self.master_relaxation = mm.get_objective()
        

        if not mm.solved:
            logging.warning("master model was not solved.")
            return None

        # BRANCHING
        if not mm.feasible:
            logging.warning("master model was not feasible.") 
            return None
                
        if mm.get_objective() >= self.best_objective:  # Check if master model is worse than best so far solution
            logging.info("master model solution ({:f}) is worse than best-so-far solution ({:f}).".format(mm.get_objective(), self.best_objective))
            return None
        if mm.is_solution_integer():  # Check if solution is integer            
                        
            if mm.get_objective() < self.best_objective:
                self.best_objective = mm.get_objective()
                logging.info("best objective was updated to: {:f}".format(self.best_objective))                
            
            return mm.get_solution_and_tasks(self.env, self.acs)
        else:
            logging.info("master model solution is not integer")
            
            # # :TODO : try master with binary vars
            # mm_bin = MasterModel(patterns, env.major_frame_length, [ac.task for ac in acs], bin_vars=True)
            # mm_bin.solve()
    
            # if mm_bin.feasible:
            #     if mm_bin.get_objective() < self.best_objective:
            #         self.best_objective = mm_bin.get_objective()
            #         # TODO : save solution somehow  

            # Create two branches and return better solution
            t_p = time.time()
            pair = get_pair(mm.get_selected_patterns(), on_same, on_diff)        
            self.time_get_pair += time.time() - t_p
            
            if pair is None:  # There was no pair to generate                
                logging.info("leaf solution was reached, but MP was not integer, use global model instead")
                t_s = time.time()
                m_global = ilp_global_solver.Solver(self.arg_parser, self.env, self.acs, on_same, on_diff)
                solution, tasks = m_global.solve()
                t_e = time.time()
                
                self.time_global_solving += t_e - t_s
                global_obj = float(solution.solver_metadata["objective"])
                if global_obj and global_obj >= 0 and global_obj < self.best_objective:
                    self.best_objective = global_obj                
                return solution, tasks                                
            else:
                logging.info("branching on pair {:s}".format(str(pair)))

            # Generate new lists
            on_same_new = on_same.copy()
            on_diff_new = on_diff.copy()
            on_diff_new.append(pair)
            on_same_new.append(pair)                                                     
            
            p_same = [p for p in patterns if ((pair[0] in p.task_mapping and pair[1] in p.task_mapping)
                                            or (pair[0] not in p.task_mapping and pair[1] not in p.task_mapping))]
            p_diff = [p for p in patterns if not (pair[0] in p.task_mapping and pair[1] in p.task_mapping)]
            
            #p_same = [p for p in patterns if (((pair[0] in p.task_mapping and pair[1] in p.task_mapping) and p.task_mapping[pair[0]] == p.task_mapping[pair[1]])
             #                               or (pair[0] not in p.task_mapping and pair[1] not in p.task_mapping))]
            #p_diff = [p for p in patterns if not (pair[0] in p.task_mapping and pair[1] in p.task_mapping) or (p.task_mapping[pair[0]] != p.task_mapping[pair[1]])]

            # - two branches
            # - on same
            rm = RecoveryModel(self.env, self.acs, on_same_new, on_diff)
            rm.solve()
            self.time_recovery += rm.solving_time + rm.init_time
            if rm.feasible:
                for p in rm.get_patterns():
                    if p.task_mapping not in [x.task_mapping for x in p_same]:
                        p_same.append(p)                
                sol_same = self.branch_and_price(on_same_new, on_diff, p_same)
            else:                
                logging.info("RecoveryModel was not feasible (on_same)")
                sol_same = None
                
            # - on diff
            rm = RecoveryModel(self.env, self.acs, on_same, on_diff_new)
            rm.solve()
            self.time_recovery += rm.solving_time + rm.init_time
            if rm.feasible:
                for p in rm.get_patterns():
                    if p.task_mapping not in [x.task_mapping for x in p_diff]:
                        p_diff.append(p)                                
                sol_diff = self.branch_and_price(on_same, on_diff_new, p_diff)
            else:
                logging.info("RecoveryModel was not feasible (on_diff)")
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
        if float(sol1[0].solver_metadata["objective"]) < float(sol2[0].solver_metadata["objective"]):
            return sol1
        else:
            return sol2
