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
        for a in self.alpha:
            if EPS < a.X < 1 - EPS:
                return False
        return True        

                     
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
        return [self.patterns[i] for i,a in enumerate(self.alpha) if a.X > 1e-4]
    
    def get_solution_and_tasks(self,
                               env: instance.Environment,
                               acs:  List[instance.AssignmentCharacteristic],
                               task_map: Mapping[str, instance.Task]) -> Tuple[instance.Solution, List[instance.Task]]:
        task_to_ra = instance.get_task_to_ra(task_map, acs)
        solution=None
        tasks=[]

        s_feasible=True if self.model.Status == grb.GRB.OPTIMAL or (
            model.Status == grb.GRB.TIME_LIMIT and model.SolCount > 0) else False
        s_solver_name="BAP-MasterModel"
        s_solution_time=int(round(self.solving_time*1000))  # to ms
        s_windows=[]
        s_metadata={"objective": -1}

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
                    task_processors = []
                    for p in task_to_ra[t].processors:  
                        window_tasks_assignments.append(instance.TaskAssignment(task=t,
                                                                                processor=p.processor,
                                                                                processing_unit=pu_allocations[p.processor],
                                                                                start=0,
                                                                                length=task_to_ra[t].length))
                        
                                                      
                        # increment the processor units
                        pu_allocations[p.processor] += p.processing_units                                
                        task_processors.append(instance.ProcessorAssignment(p.processor, p.processing_units))                                 
                                
                    tasks.append(instance.Task(name=t,
                                               command=task_map[t].command,                                                
                                               length=task_to_ra[t].length,
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
        return lst[0]  # TODO: implement some heuristic
    
    all_tasks = set()
    for p in selected_patterns:
        all_tasks.update(p.task_mapping.keys())
    
    all_pairs = itertools.combinations(all_tasks, 2)  # combine the tasks
    all_pairs = [p for p in all_pairs if p not in on_same and p not in on_diff]  # filter already used tasks
    
    if all_pairs:
        return pair_selection_heuristis(all_pairs)
    else:
        return None

 
class SubproblemModelILP(ILPSolver):
    
    def __init__(self, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], dual_prices: Tuple[float, Mapping[str, float]]):
        self.env = env
        self.acs = acs
        self.dual_prices = dual_prices 
        self.x_ik = None       
        self.l = None
        
        self._init_model()        
        
    def _init_model(self):
        m = grb.Model("Subproblem-ILP")
        num_tasks = len(self.acs)

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
        
       
class Solver:

    def __init__(self, arg_parser: ap.ArgParser, env: instance.Environment, acs: List[instance.AssignmentCharacteristic]):
        self.arg_parser = arg_parser
        self.env = env
        self.acs = acs
        self.patterns = None

    def solve(self) -> Tuple[instance.Solution, List[instance.Task]]:

        # TODO

        solution = None 
        tasks = None       
        return (solution, tasks)
    
    def init_patterns(self):
        pass
    
    def master_model(self):
        pass        
