#! /usr/bin/python3
from common import arg_parser as ap
from common import instance
from typing import List, Tuple, Mapping
from ilp_global_solver import ilp_global_solver
from ilp_fixed_solver import ilp_fixed_solver
import gurobipy as grb
import sys
import time
import itertools
from numpy import random
import logging
from common.union_find import UnionFind
from enum import Enum

class BranchingType(Enum):
    ON_PAIRS = 1  # pos_branch ~ pairs of tasks to be in the same window, neg_branch ~ pairs to be in different windows
    ON_TASKS = 2  # pos_branch ~ fix task to acs idx assignment, neg_branch ~ task cannot be on given resource

class OnPairsBranch(Enum):
    IN_SAME = 1
    IN_DIFF = 2

class BranchingRule:
    
    def __init__(self):
        pass
        
    def constrain_global_model(self, model: grb.Model, x_ijk: grb.tupledict, windows_ub: int):
        """Add constraints to the global model according to this Branching Rule"""
        raise NotImplementedError
    
    def constrain_recovery_model(self, model: grb.Model, x_ijk: grb.tupledict, windows_ub: int):
        """Add constraints to the recovery model according to this Branching Rule"""
        raise NotImplementedError
    
    def constrain_subproblem_model(self, model: grb.Model, x_ik: grb.tupledict):
        """Add constraints to the subproblem model according to this Branching Rule"""
        raise NotImplementedError
    
    def filter_patterns(self, patterns: List[instance.Pattern]) -> List[instance.Pattern]:
        """Take old patterns and filter the ones that are not respecting this BranchingRule"""
        raise NotImplementedError
    
    def get_branching_rules(self) -> List['BranchingRule']:
        """Generate a list of new Branching Rules"""
        raise NotImplementedError
    
    def get_string_representation(self) -> str:
        raise NotImplementedError

class OnTaskBranchingRule(BranchingRule):    
    def __init__(self):
        self.fixed_task_mapping = {}  # task -> acs idx
        self.remaining_tasks = None
        self.acs = None
        self.task_to_idx = None
        
    def initialize(self, acs: List[instance.AssignmentCharacteristic], task_to_idx: Mapping[str, int]):
        self.acs = acs
        self.task_to_idx = task_to_idx
        self.remaining_tasks = [x.task for x in acs]
        procs = {x.task: x.resource_assignmnets[0].length for x in acs}        
        self.remaining_tasks.sort(key=lambda x: procs[x], reverse=False)  # Sort the tasks by non-decreasing proc time on res. 0
        self.task_to_idx = task_to_idx
        
        return self
        
    def _initialize_all(self, fixed_task_mapping: Mapping[str,int], remaining_tasks: List[str], acs: List[instance.AssignmentCharacteristic], task_to_idx: Mapping[str,int]):
        self.fixed_task_mapping = fixed_task_mapping
        self.remaining_tasks = remaining_tasks
        self.acs = acs
        self.task_to_idx = task_to_idx
        
        return self
                        
    def constrain_global_model(self, model: grb.Model, x_ijk: grb.tupledict, windows_ub: int):
        """Add constraints to the global model according to this Branching Rule"""
        for t, k_fix in self.fixed_task_mapping.items():
            i = self.task_to_idx[t]            
            model.addConstr(x_ijk.sum(i, "*", k_fix) == 1)        
    
    def constrain_recovery_model(self, model: grb.Model, x_ijk: grb.tupledict, windows_ub: int):
        """Add constraints to the recovery model according to this Branching Rule"""
        for t, k_fix in self.fixed_task_mapping.items():
            i = self.task_to_idx[t]            
            model.addConstr(x_ijk.sum(i, "*", k_fix) == 1)
    
    def constrain_subproblem_model(self, model: grb.Model, x_ik: grb.tupledict):
        """Add constraints to the subproblem model according to this Branching Rule"""
        for t in self.fixed_task_mapping:
            i = self.task_to_idx[t]            
            k_fix = self.fixed_task_mapping[t]
            model.addConstr(grb.quicksum(x_ik[i,k] for k in range(len(self.acs[i].resource_assignmnets)) if k != k_fix) == 0)
    
    def filter_patterns(self, patterns: List[instance.Pattern]) -> List[instance.Pattern]:
        """Take old patterns and filter the ones that are not respecting this BranchingRule"""
        filtered_patterns = []        
        for p in patterns:
            skip_pattern = False
            for t in p.task_mapping:
                if t in self.fixed_task_mapping and p.task_mapping[t] != self.fixed_task_mapping[t]:
                    skip_pattern = True
                    break
            
            if skip_pattern:
                continue
            else:
                filtered_patterns.append(p)
        return filtered_patterns
    
    def get_string_representation(self) -> str:
        return "fixed_task_mapping={:s}".format(str(self.fixed_task_mapping))
    
    def get_branching_rules(self) -> List['BranchingRule']:
        """Generate a list of new Branching Rules"""
        if not self.remaining_tasks:
            return []
        else:
            task = self.remaining_tasks[0]        
            
            all_assignments = list(range(len(self.acs[self.task_to_idx[task]].resource_assignmnets)))
            #lengths = {i: self.acs[self.task_to_idx[task]].resource_assignmnets[i].length for i in all_assignments}
            #all_assignments.sort(key=lambda x: lengths[x])  # sort the assignments from the shortest one
            slopes = {i: self.acs[self.task_to_idx[task]].resource_assignmnets[i].slope for i in all_assignments}
            all_assignments.sort(key=lambda x: slopes[x])  # sort the assignments from the smallest slope            
            
            branches = []
            for k in all_assignments:
                new_mapping = self.fixed_task_mapping.copy()
                new_mapping[task] = k
                
                branches.append(OnTaskBranchingRule()._initialize_all(                    
                    new_mapping,
                    self.remaining_tasks[1:],
                    self.acs,
                    self.task_to_idx)
                )
            return branches                            

class OnPairsBranchingRule(BranchingRule):    
    def __init__(self):
        super().__init__()
        self.in_same = []
        self.in_diff = []
        self.uf = None
        self.used_by_diff = None
        self.task_to_idx = None
        self.branch_type = None
        self.task_counter = None
        self.remaining_pairs = None        
    
    def initialize(self, uf: UnionFind, task_to_idx: Mapping[str, int]):
        self.uf = uf
        self.task_to_idx = task_to_idx        
        self.task_counter = {t: 0 for t in task_to_idx.keys()}
        self.remaining_pairs = list(itertools.combinations(task_to_idx.keys(), 2))
        self.used_by_diff = set()    
        
        return self    
        
    def _initialize_all(self, in_same: List[Tuple[str,str]], in_diff: List[Tuple[str,str]], 
                       uf: UnionFind, used_by_diff: set, task_to_idx: Mapping[str,int], 
                       branch_type: OnPairsBranch, task_counter: Mapping[str,int], remaining_pairs: List[Tuple[str,str]]):
        self.in_same = in_same
        self.in_diff = in_diff
        self.uf = uf
        self.used_by_diff = used_by_diff
        self.task_to_idx = task_to_idx
        self.branch_type = branch_type
        self.task_counter = task_counter
        self.remaining_pairs = remaining_pairs
        
        return self
        
    def constrain_global_model(self, model: grb.Model, x_ijk: grb.tupledict, windows_ub: int):
        """Add constraints to the global model according to this Branching Rule"""                                        
        for t1, t2 in self.in_same:                
            model.addConstrs(x_ijk.sum(self.task_to_idx[t1], j, "*") == x_ijk.sum(self.task_to_idx[t2], j, "*")
                                for j in range(windows_ub))                
                    
        for t1, t2 in self.in_diff:                
            model.addConstrs(x_ijk.sum(self.task_to_idx[t1], j, "*") + x_ijk.sum(self.task_to_idx[t2], j, "*") <= 1
                                for j in range(windows_ub))                
    
    def constrain_recovery_model(self, model: grb.Model, x_ijk: grb.tupledict, windows_ub):
        """Add constraints to the recovery model according to this Branching Rule"""
        for t1, t2 in self.in_same:
            model.addConstrs(x_ijk.sum(self.task_to_idx[t1], j, "*") == x_ijk.sum(self.task_to_idx[t2], j, "*")
                             for j in range(windows_ub))
            
        for t1, t2 in self.in_diff:
            model.addConstrs(x_ijk.sum(self.task_to_idx[t1], j, "*") + x_ijk.sum(self.task_to_idx[t2], j, "*") <= 1
                             for j in range(windows_ub))
    
    def constrain_subproblem_model(self, model: grb.Model, x_ik: grb.tupledict):
        """Add constraints to the subproblem model according to this Branching Rule"""        
        for t1, t2 in self.in_same:            
            model.addConstr(x_ik.sum(self.task_to_idx[t1], "*") == x_ik.sum(self.task_to_idx[t2],"*"))

        for t1, t2 in self.in_diff:            
            model.addConstr(x_ik.sum(self.task_to_idx[t1], "*") + x_ik.sum(self.task_to_idx[t2],"*") <= 1 ) 
    
    def filter_patterns(self, patterns: List[instance.Pattern]) -> List[instance.Pattern]:
        """Take old patterns and filter the ones that are not respecting this BranchingRule"""
        if self.branch_type == OnPairsBranch.IN_SAME:
            pair = self.in_same[-1]  # current branching pair to use for the filtering
            filtered_patterns = [p for p in patterns if ((pair[0] in p.task_mapping and pair[1] in p.task_mapping)
                                            or (pair[0] not in p.task_mapping and pair[1] not in p.task_mapping))]
        elif self.branch_type == OnPairsBranch.IN_DIFF:
            pair = self.in_diff[-1]  # current branching pair to use for the filtering
            filtered_patterns = [p for p in patterns if not (pair[0] in p.task_mapping and pair[1] in p.task_mapping)]
        else:
            raise RuntimeError("Branching type {:s} is not supported".format(str(self.branch_type)))
        
        return filtered_patterns
    
    def get_string_representation(self) -> str:
        return "in_same={:s} \nin_diff={:s}".format(str(self.in_same), str(self.in_diff))
        
    
    def get_branching_rules(self) -> List[BranchingRule]:
        """Generate a list of new Branching Rules"""        
        if not self.remaining_pairs:  # There is no remaining pair to branch on
            return []
        else:
            pair = self.remaining_pairs[0]  # currently selected branching pair
                
            # on same branch
            b_same = OnPairsBranchingRule()._initialize_all(
                self.in_same + [pair],
                self.in_diff,
                self.uf.get_copy(),
                self.used_by_diff,
                self.task_to_idx,
                OnPairsBranch.IN_SAME,
                self.task_counter.copy(),
                self.remaining_pairs[1:]
            )
            
            b_same.uf.union(self.task_to_idx[pair[0]], self.task_to_idx[pair[1]])   
            b_same.task_counter[pair[0]] += 1
            b_same.task_counter[pair[1]] += 1                     
                        
            b_same.remaining_pairs = [p for p in b_same.remaining_pairs if not b_same.uf.find(self.task_to_idx[p[0]], self.task_to_idx[p[1]])]                        
            b_same.remaining_pairs.sort(key=lambda x: b_same.task_counter[x[0]] + b_same.task_counter[x[1]], reverse=False)                        
            
            # on diff branch 
            b_diff = OnPairsBranchingRule()._initialize_all(
                self.in_same,
                self.in_diff + [pair],
                self.uf.get_copy(),
                self.used_by_diff | set([(self.uf._root(self.task_to_idx[pair[0]]), self.uf._root(self.task_to_idx[pair[1]])),
                                         (self.uf._root(self.task_to_idx[pair[1]]), self.uf._root(self.task_to_idx[pair[0]]))]),
                self.task_to_idx,
                OnPairsBranch.IN_DIFF,
                self.task_counter.copy(),
                self.remaining_pairs[1:]
            )
            b_diff.task_counter[pair[0]] += 1
            b_diff.task_counter[pair[1]] += 1                     
            b_diff.remaining_pairs = [p for p in b_diff.remaining_pairs if (b_diff.uf._root(self.task_to_idx[p[0]]), 
                                                                            b_diff.uf._root(self.task_to_idx[p[1]])) not in b_diff.used_by_diff]
            b_diff.remaining_pairs.sort(key=lambda x: b_diff.task_counter[x[0]] + b_diff.task_counter[x[1]], reverse=False)
            
            return [b_same, b_diff]
    

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
        super().__init__()
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
        s_metadata={"objective": str(float("inf"))}

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


class SubproblemModelILP(ILPSolver):
    
    def __init__(self, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], dual_prices: Tuple[float, Mapping[str, float]], timelimit: float=float("inf")):
        super().__init__()
        self.env = env
        self.acs = acs
        self.dual_prices = dual_prices         
        self.x_ik = None       
        self.l = None        
        self.timelimit = timelimit
        self.task_to_idx = None
        
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
        self.task_to_idx = task_to_idx

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
    
    def forbid_assignment(self, assignment: Mapping[str, int]):        
        # if we have binary variables x, y, z
        # and the assignment we want to forbid is x=0, y=1, z=0
        # we construct formula (1-x) + y + (1-z) < 3
        # -> 2 + (-x -y -z) + 2y < 3
        # -> - sum (all variables) + 2*(positive vars) < number of positive vars
        expr = -self.x_ik.sum("*", "*")        
        
        for t in assignment:
            t_idx = self.task_to_idx[t]
            expr += 2 * self.x_ik[t_idx, assignment[t]]
        
        self.model.addConstr(expr <= len(assignment)-1)
    
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
        if p_task_mapping:                             
            cost = pattern.compute_cost(self.acs)
        else:
            cost = 0
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
    def __init__(self, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], timelimit: float=float("inf")):
        super().__init__()
        self.env = env
        self.acs = acs         
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
        
        # - symmetry breaker
        m.addConstrs(l_j[j] >= l_j[j+1] for j in range(num_tasks-1))
        #m.addConstrs(grb.quicksum(x_ijk[i,j,k]*j for j in range(num_tasks) for k in range(len(self.acs[i].resource_assignmnets)))
        #             <= grb.quicksum(x_ijk[i+1,j,k]*j for j in range(num_tasks) for k in range(len(self.acs[i+1].resource_assignmnets)))
        #             for i in range(num_tasks-1))        
        
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

    def __init__(self, arg_parser: ap.ArgParser, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], init_data_path: str, timelimit: float=float("inf"), branching_type: BranchingType=BranchingType.ON_PAIRS):
        self.arg_parser = arg_parser
        self.env = env
        self.acs = acs
        self.task_to_ac = instance.get_task_to_acs_map(self.acs)
        self.init_data_path = init_data_path
        self.patterns = None
        self.timelimit = timelimit
        self.time_start = None
        self.branching_type = branching_type
                
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
            rm = RecoveryModel(self.env, self.acs, timelimit=self._get_remaining_time())
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
            init_obj = self.best_objective
            logging.info("INIT OBJ" + str(init_obj))
            
            # Start beanch-and-price
            t_start=time.time()            
            if self.branching_type == BranchingType.ON_TASKS:
                b_rule = OnTaskBranchingRule().initialize(self.acs, {a.task: i for i, a in enumerate(self.acs)})
            elif self.branching_type == BranchingType.ON_PAIRS:                
                b_rule = OnPairsBranchingRule().initialize(UnionFind(len(self.acs)), {a.task: i for i, a in enumerate(self.acs)})            
            else:
                raise RuntimeError("Branching type {:s} is not known".format(str(self.branching_type)))            
            bap_s = self.branch_and_price(b_rule, patterns)
            t_end=time.time()

            self.solving_time = int((t_end - t_start) * 1000)  # to ms
                    
            logging.info("search ended")
            logging.info("solution quality {:f}".format(self.best_objective))            
            
            EPS = 1e-4
            #if bab_s and abs(self.best_objective - init_obj) > EPS:  # use the initial solution if nothing better was found                
            if bap_s and self.best_objective < init_obj - EPS:  # use the initial solution if nothing better was found                
                sol, tasks = bap_s
        else:        
            logging.info("no initial solution was provided/found")
            sol = instance.Solution(False, "BAP", self.solving_time, {}, [])
            tasks = []
            
        t_e = time.time()
        
        sol.solution_time = int(round((t_e - t_s) * 1000)) 
        sol.solver_name = "BAP_" + self.branching_type.name       
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

    def branch_and_price(self, b_rule: BranchingRule, patterns: List[instance.Pattern]):
        logging.info("branching\n{:s}".format(b_rule.get_string_representation()))
        if not self._get_remaining_time():  # reamining time is 0
            logging.warning("timelimit was reached; exiting the branch")
            self.interrupted = True
            return None
        
        self.number_of_nodes += 1
        env = self.env 
        acs = self.acs      
        tasks = [ac.task for ac in acs]
                                
        logging.info("PATTERNS {:d}".format(len(patterns)))
        for p in patterns:
            logging.info("    {:s}".format(str(p.to_dict())))

        # Iterate - master -> subproblem
        n_patterns = 0
        last_pattern_mapping = None
        ss_forbidden = []
        while True:            
            # - solve restricted master problem
            mm = MasterModel(patterns, env.major_frame_length, tasks, timelimit=self._get_remaining_time())            
            mm.model.setParam("Presolve", 0)  # TODO: experimental (might help with some numerical issues)
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
            ss = SubproblemModelILP(env, acs, (pi0, pit), timelimit=self._get_remaining_time())
            b_rule.constrain_subproblem_model(ss.model, ss.x_ik)
            
            # forbid assignments, which repeated (due to numeric problems?)
            for f_a in ss_forbidden:
                ss.forbid_assignment(f_a)
            
            ss.solve()
            
            if ss.time_limit_reached():
                self.interrupted = True
                return None
            else:
                relaxation = mm.get_objective() + ss.model.ObjVal
                if relaxation > self.best_objective:
                    logging.info("Relaxation {:s} is worse than best obj {:s}".format(str(relaxation), str(self.best_objective)))
            
            # - stats info (subproblem)
            self.time_sub_init += ss.init_time
            self.time_sub_solving += ss.solving_time 
            
            if not ss.feasible:
                logging.warning("subproblem model is not feasible.")
                return None
                        
            EPS = 1e-4
            if ss.model.ObjVal >= -EPS:  # no more improving patterns exist
                logging.info("subproblem objective was non-negative; ending the iteration.")
                break                                    
            else:
                p = ss.get_pattern()
                logging.info("  found pattern {:s}, {:s}".format(str(p.to_dict()), str(ss.model.ObjVal)))
                
                if p.task_mapping == last_pattern_mapping:
                    logging.info("  warning - task mapping of the last pattern is the same as the current one {:s}".format(str(p.task_mapping)))
                    # forbid the assignment in the future subproblems
                    ss_forbidden.append(p.task_mapping)
                    continue
                    # previously used: just break and hope it will be ok
                    #logging.info("          - breaking the iteration (assuming it is just about numerical issues")
                    ## TODO: optimal = false (possibly?)
                    #self.interrupted = True
                    #break
                
                patterns.append(p)    
                last_pattern_mapping = p.task_mapping  
                n_patterns += 1                                        
        # END of pattern generation phase ----------------------------------------------------------------------------------
        
        self.patterns_generated_num.append(n_patterns)

        # Solve master model to get the optimal solution of the relaxed problem
        # - solve restricted master problem        
        mm = MasterModel(patterns, env.major_frame_length, [ac.task for ac in acs], timelimit=self._get_remaining_time())
        mm.solve()  
        mm_obj = mm.get_objective()                     
               
        if mm.time_limit_reached():
            logging.warning("master model reached timelimit.")
            self.interrupted = True
            return None
                
        # - stats info (master)
        self.time_masters_init += mm.init_time
        self.time_masters_solving += mm.solving_time
        
        if self.number_of_nodes == 1:  # root node
            self.master_relaxation = mm_obj
        
        if not mm.solved:
            logging.warning("master model was not solved.")
            return None

        # BRANCHING
        if not mm.feasible:
            logging.warning("master model was not feasible.") 
            return None
                
        if mm_obj >= self.best_objective:  # Check if master model is worse than best so far solution
            logging.info("master model solution ({:f}) is pruned by best-so-far solution ({:f}).".format(mm.get_objective(), self.best_objective))
            return None
        if mm.is_solution_integer():  # Check if solution is integer                                    
            if mm_obj < self.best_objective:
                self.best_objective = mm_obj
                logging.info("best objective was updated to: {:f}".format(self.best_objective))                
            
            return mm.get_solution_and_tasks(self.env, self.acs)
        else:
            logging.info("master model solution is not integer")
            
            new_rules = b_rule.get_branching_rules()                    
                                    
            if not new_rules:  # No new rules could be generated
                logging.info("leaf solution was reached, but MP was not integer, use global model instead")
                t_s = time.time()
                if self.branching_type == BranchingType.ON_TASKS:  # use dedicated model for fixed assignment
                    m_global = ilp_fixed_solver.Solver(self.arg_parser, self.env, self.acs, b_rule.fixed_task_mapping, timelimit=self._get_remaining_time(), cutoff=self.best_objective if self.best_objective else None)
                    solution, tasks = m_global.solve()
                else:  # use generic form for other types of branching
                    m_global = ilp_global_solver.Solver(self.arg_parser, self.env, self.acs, timelimit=self._get_remaining_time())
                    b_rule.constrain_global_model(m_global.model, m_global.x_ijk, len(self.acs))
                    solution, tasks = m_global.solve()
                t_e = time.time()
                
                self.time_global_solving += t_e - t_s
                global_obj = float(solution.solver_metadata["objective"])
                if global_obj and global_obj >= 0 and global_obj < self.best_objective:
                    self.best_objective = global_obj  
                    logging.info("best objective was updated to (by global): {:f}".format(self.best_objective))                

                    
                if m_global.model.Status == grb.GRB.TIME_LIMIT:                    
                    self.interrupted = True
                                  
                return solution, tasks                                
            else:  # some rules exist; try branching                
                best_branch_obj = float("inf")
                best_branch_sol = None

                for rule in new_rules:
                    rm = RecoveryModel(self.env, self.acs, timelimit=self._get_remaining_time())
                    rule.constrain_recovery_model(rm.model, rm.x, len(self.acs))
                    rm.solve()
                    self.time_recovery += rm.solving_time + rm.init_time
                    
                    if rm.model.Status == grb.GRB.TIME_LIMIT:
                        logging.info("Timelimit reached for recovery model.")
                        self.interrupted = True
                        break
                    
                    if not rm.feasible:
                        logging.info("RecoveryModel was not feasible for {:s}".format(rule.get_string_representation()))                
                        continue
                    else:        
                        rm_patterns = rm.get_patterns()
                        rm_obj = sum([p.cost for p in rm_patterns]) / self.env.major_frame_length
                        
                        rm_solution = instance.Solution(True, "BAP", time.time() - self.time_start,
                                                {"objective": str(rm_obj)}, 
                                                [p.to_window(self.env, self.task_to_ac) for p in rm_patterns])
                        rm_tasks = instance.patterns_to_task(rm_patterns, self.task_to_ac)    
                                                
                        if rm_obj < self.best_objective:  # Check if objective of reconstructed solution is better
                            self.best_objective = rm_obj
                            logging.info("best objective was updated to (by RM): {:f}".format(self.best_objective))                                                                
                        
                        if rm_obj <= mm_obj:  # prune this node if integer solution equal to relaxed solution was found                                               
                            return (rm_solution, rm_tasks)
                        
                        if rm_obj < best_branch_obj:
                            best_branch_obj = rm_obj
                            best_branch_sol = (rm_solution, rm_tasks)
                        
                        filtered_patterns = rule.filter_patterns(patterns)  # filter patterns by new rule
                        for p in rm_patterns:
                            # add recovery patterns if not already there
                            if p.task_mapping not in [x.task_mapping for x in filtered_patterns]:
                                filtered_patterns.append(p)                
                        # branch
                        sol = self.branch_and_price(rule, filtered_patterns)                        
                        if sol and float(sol[0].solver_metadata["objective"]) < best_branch_obj:
                            best_branch_obj = float(sol[0].solver_metadata["objective"])
                            best_branch_sol = sol
                
                return best_branch_sol
            