#! /usr/bin/python3
from common import arg_parser as ap
from common import instance
from typing import List, Tuple, Mapping
import gurobipy as grb
import sys
import time


class MasterModel:
    def __init__(self, patterns: List[instance.Pattern], major_frame_length: int, tasks: List[str]):
        self.model = None
        self.alpha = None
        self.patterns = patterns
        self.major_frame_length = major_frame_length
        self.tasks = tasks
        self.c0 = None
        self.ct = {}
        self.solved = False
        self.feasible = False
        
        self._init_model()
        
    def _init_model(self):
        m = grb.Model("Master Model")
        
        # variables
        alpha = m.addVars(len(self.patterns), vtype=grb.GRB.CONTINUOUS, lb=0, name="alpha")
        
        # constraints
        # - major frame length        
        self.c0 = m.addConstr(grb.quicksum(alpha[i] * p.length for i, p in enumerate(self.patterns)) <= self.major_frame_length, name="C:major_frame")
        
        # - patterns cover tasks
        for t in self.tasks:                        
            self.ct[t] = m.addConstr(grb.quicksum(alpha[i] for i, p in enumerate(self.patterns) if t in p.task_mapping) >= 1, 
                                                  name="C:task_cover_{}".format(t))
        
        # objective
        m.setObjective(grb.quicksum(alpha[i] * p.cost for i, p in enumerate(self.patterns)), sense=grb.GRB.MINIMIZE)
        
        self.model = m
        self.alpha = alpha
        
    def solve(self):
        t_start=time.time()
        self.model.optimize()
        t_end=time.time()
        
        s_feasible=True if self.model.Status == grb.GRB.OPTIMAL or (
            self.model.Status == grb.GRB.TIME_LIMIT and self.model.SolCount > 0) else False
        
        self.solved = True
        self.feasible = s_feasible        
        
    def get_dual_prices(self) -> Tuple[float, Mapping[str, float]]:
        if not self.solved:
            print("warning: get_dual_prices cannot be called for unsolved model; call solve() first", file=sys.stderr)
        if not self.feasible:
            print("warning: model is not feasible, dual prices cannot be obtained", file=sys.stderr)
        return self.c0.Pi, {t: self.ct[t].Pi for t in self.tasks}
        
        
class Solver:

    def __init__(self, arg_parser: ap.ArgParser, env: instance.Environment, acs: List[instance.AssignmentCharacteristic]):
        self.arg_parser = arg_parser
        self.env = env
        self.acs = acs
        self.patterns = None

    def solve(self) -> Tuple[instance.Solution, List[instance.Task]]:
        
        
        
        
        solution = None 
        tasks = None       
        return (solution, tasks)
    
    def init_patterns(self):
        pass
    
    def master_model(self):
        pass        
