#! /usr/bin/python3
from common import arg_parser as ap
from common import instance
from typing import List, Tuple
import gurobipy as grb
import sys
import time
import numpy as np

# ###
# Coefficients:
# ───────────────────────────────────────────────────────────────
#        Coef.  Std. Error      t  Pr(>|t|)  Lower 95%  Upper 95%
# ───────────────────────────────────────────────────────────────
# X1  0.291156   0.0268019  10.86    <1e-24   0.238534   0.343778  slope A53
# X2  1.21833    0.0655871  18.58    <1e-62   1.08955    1.3471    intercept A53
# X3  0.481873   0.0258129  18.67    <1e-62   0.431192   0.532553  slope A72
# X4  0.55007    0.0397989  13.82    <1e-37   0.471929   0.62821   intercept A72
# ───────────────────────────────────────────────────────────────
###
def get_coeff(which: str, res: str):
    if res == "A53":
        if which == "slope":
            return 0.291156
        elif which == "intercept":
            return 1.21833
        else:
            return 0 
    elif res == "A72":
        if which == "slope":
            return 0.481873
        elif which == "intercept":
            return 0.55007
        else:
            return 0
    else:
        return 0

class Solver:

    def __init__(self, arg_parser: ap.ArgParser, env: instance.Environment, acs: List[instance.AssignmentCharacteristic]):
        self.arg_parser = arg_parser
        self.env = env
        self.acs = acs

        self.model = None
        self.x = None
        self.l = None

        task_lengths = [ra.length for ac in acs for ra in ac.resource_assignmnets]
        self.n_win_ub = min(np.argmax(np.cumsum(task_lengths) > env.major_frame_length), len(acs))

        self._init()

    def _init(self):
        n_tasks = len(self.acs)
        n_win_ub = self.n_win_ub
        env = self.env
        n_solts = sum([p.processing_units for p in env.processors_list])

        model = grb.Model()

        # VARIABLES
        # x_ijks variables        
        # Task Ti in windows Wj on resource Rk slot s (global core idx)
        x_ijks = model.addVars([(i, j, k, s)
                               for i in range(n_tasks)
                               for j in range(n_win_ub)
                               for k in range(len(self.acs[i].resource_assignmnets))
                               for s in range(n_solts)],
                               vtype=grb.GRB.BINARY,
                               name="x")        

        # length of slot in window
        l_js = model.addVars([(j,s) for j in range(n_win_ub) for s in range(n_solts)], vtype=grb.GRB.CONTINUOUS, name="l")

        # difference of length of consecutive slots
        d_js = model.addVars([(j,s) for j in range(n_win_ub) for s in range(n_solts)], vtype=grb.GRB.CONTINUOUS, name="d")
 
       
        # CONSTRAINTS
        # - each task assigned to one of the slots
        model.addConstrs(x_ijks.sum(i, "*", "*", "*") == 1 
            for i in range(n_tasks))

        # - each slot at most one task
        model.addConstrs(x_ijks.sum("*", j, "*", s) <= 1 
            for j in range(n_win_ub) for s in range(n_solts))
        
        # get length of each slot
        model.addConstrs(l_js[j,s] == grb.quicksum(x_ijks[i,j,k,s] * self.acs[i].resource_assignmnets[k].length for i in range(n_tasks) for k in range(len(self.acs[i].resource_assignmnets)))
            for j in range(n_win_ub) for s in range(n_solts))

        # order the solts >= (length)
        model.addConstrs(l_js[j,s] >= l_js[j, s+1]
            for j in range(n_win_ub) for s in range(n_solts - 1)
        )
    
        # get differences
        model.addConstrs( d_js[j,s] == l_js[j,s] - l_js[j,s+1]
            for j in range(n_win_ub) for s in range(n_solts - 1)
        )

        # - last difference fixed to length of the last slot
        model.addConstrs(d_js[j,n_solts - 1] == l_js[j,n_solts - 1]
            for j in range(n_win_ub)
        )

        # respect capacity of each cluster
        model.addConstrs( grb.quicksum(x_ijks[i,j,k,s] * p.processing_units for i in range(n_tasks) for k in range(len(self.acs[i].resource_assignmnets)) for s in range(n_solts) for p in self.acs[i].resource_assignmnets[k].processors if env.processors_list[r_id].name == p.processor) <= env.processors_list[r_id].processing_units
            for j in range(n_win_ub) for r_id in range(len(env.processors_list))
        )

        # respect the major frame length
        model.addConstr(grb.quicksum(l_js[j,0] for j in range(n_win_ub)) <= self.env.major_frame_length)

        # - window ordering constraint (symmetry pruning)
        model.addConstrs((l_js[j,0] >= l_js[j+1,0] for j in range(n_win_ub-1)))


        # specity the objective
        obj = grb.quicksum(
            d_js[j,s] * grb.quicksum(x_ijks[i,j,k,s_] * (self.acs[i].resource_assignmnets[k].slope * get_coeff("slope", self.acs[i].resource_assignmnets[k].processors[0].processor) + self.acs[i].resource_assignmnets[k].intercept * get_coeff("intercept", self.acs[i].resource_assignmnets[k].processors[0].processor))
                        for i in range(n_tasks) for k in range(len(self.acs[i].resource_assignmnets)) for s_ in range(s+1)
                        )
            for j in range(n_win_ub) for s in range(n_solts)
        )

        model.setObjective(obj/env.major_frame_length, sense=grb.GRB.MINIMIZE)

        self.model = model
        self.x = x_ijks
        self.l = [l_js[j,0] for j in range(n_win_ub)]


    def solve(self) -> Tuple[instance.Solution, List[instance.Task]]:
        num_tasks = len(self.acs)
        windows_ub = self.n_win_ub
        n_solts = sum([p.processing_units for p in self.env.processors_list])
        model = self.model
        env = self.env

        # OPTIMIZE THE MODEL
        t_start=time.time()
        model.optimize()
        t_end=time.time()

        solution=None
        tasks=[]

        s_feasible=True if model.SolCount > 0 else False
        s_solver_name="ILP global regression"
        s_solution_time=int(round((t_end - t_start)*1000))  # to ms
        s_windows=[]
        s_metadata={"objective": "-1"}

        x_ijk = {}
        for i in range(num_tasks):
            for j in range(windows_ub):
                for k in range(len(self.acs[i].resource_assignmnets)):
                    for s in range(n_solts):
                        if self.x[i,j,k,s].X > 0.5:
                            x_ijk[i,j,k] = True
                            break


        if s_feasible:
            s_metadata["objective"] = str(model.ObjVal)
            for j in range(windows_ub):
                window_length=int(round(self.l[j].X))
                window_tasks_assignments=[]
                if window_length < 1:
                    continue

                # processor-unit allocation (start with all processors empty)
                pu_allocations={p.name: 0 for p in env.processors_list}

                for i in range(num_tasks):
                    push_task=False
                    task_characteristic=self.acs[i]
                    task_processors=[]
                    task_length=-1
                    task_ass_idx = -1
                    
                    for k, ac in enumerate(task_characteristic.resource_assignmnets):
                        if (i, j, k) in x_ijk:
                            task_ass_idx = k
                            push_task=True                            
                            for p in ac.processors:
                                window_tasks_assignments.append(instance.TaskAssignment(task=task_characteristic.task,
                                                                                        processor=p.processor,
                                                                                        processing_unit=pu_allocations[p.processor],
                                                                                        start=0,
                                                                                        length=ac.length))

                                # increment the processor units
                                pu_allocations[p.processor] += p.processing_units
                                                                
                                task_processors.append(instance.ProcessorAssignment(
                                    p.processor, p.processing_units))
                                task_length=ac.length


                    if push_task:
                        tasks.append(instance.Task(name=task_characteristic.task,
                                                   command=task_characteristic.command,
                                                   length=task_length,
                                                   assignment_index=task_ass_idx,
                                                   processors=task_processors))                    
            
                s_windows.append(instance.Window(window_length, window_tasks_assignments))
        else:  # infeasible solution            
            s_feasible=False
    
        solution = instance.Solution(s_feasible, s_solver_name, s_solution_time, s_metadata, s_windows)
        
        return (solution, tasks)


class SolverUpperBound:

    def __init__(self, arg_parser: ap.ArgParser, env: instance.Environment, acs: List[instance.AssignmentCharacteristic]):
        self.arg_parser = arg_parser
        self.env = env
        self.acs = acs

        self.model = None
        self.x = None
        self.l = None

        task_lengths = sorted([ra.length for ac in acs for ra in ac.resource_assignmnets])
        self.n_win_ub = min(np.argmax(np.cumsum(task_lengths) > env.major_frame_length), len(acs))
        #self.n_win_ub = len(acs)

        print("Tasks lengths")
        print(task_lengths)


        self._init()

    def _init(self):
        n_tasks = len(self.acs)
        n_win_ub = self.n_win_ub
        env = self.env
        
        print(n_win_ub)

        model = grb.Model()

        # VARIABLES
        # x_ijk variables        
        # Task Ti in windows Wj on resource Rk
        x_ijk = model.addVars([(i, j, k)
                               for i in range(n_tasks)
                               for j in range(n_win_ub)
                               for k in range(len(self.acs[i].resource_assignmnets))],
                               vtype=grb.GRB.BINARY,
                               name="x")        

        # length of slot in window
        l_j = model.addVars(range(n_win_ub), vtype=grb.GRB.CONTINUOUS, name="l")
       
        # CONSTRAINTS
        # - each task assigned to one of the slots
        model.addConstrs(x_ijk.sum(i, "*", "*") == 1 
            for i in range(n_tasks))

        # get length of each window (ub)
        model.addConstrs(l_j[j] >= x_ijk[i,j,k] * self.acs[i].resource_assignmnets[k].length
            for i in range(n_tasks) for j in range(n_win_ub) for k in range(len(self.acs[i].resource_assignmnets)))

        
        # respect capacity of each cluster
        model.addConstrs( grb.quicksum(x_ijk[i,j,k] * p.processing_units for i in range(n_tasks) for k in range(len(self.acs[i].resource_assignmnets)) for p in self.acs[i].resource_assignmnets[k].processors if env.processors_list[r_id].name == p.processor) <= env.processors_list[r_id].processing_units
            for j in range(n_win_ub) for r_id in range(len(env.processors_list))
        )

        # respect the major frame length
        model.addConstr(grb.quicksum(l_j[j] for j in range(n_win_ub)) <= self.env.major_frame_length)

        # - window ordering constraint (symmetry pruning)
        model.addConstrs((l_j[j] >= l_j[j+1] for j in range(n_win_ub-1)))


        # specity the objective
        obj = grb.quicksum(
            l_j[j] * grb.quicksum(x_ijk[i,j,k] * (self.acs[i].resource_assignmnets[k].slope * get_coeff("slope", self.acs[i].resource_assignmnets[k].processors[0].processor) + self.acs[i].resource_assignmnets[k].intercept * get_coeff("intercept", self.acs[i].resource_assignmnets[k].processors[0].processor))
                        for i in range(n_tasks) for k in range(len(self.acs[i].resource_assignmnets)))
            for j in range(n_win_ub))

        model.setObjective(obj/env.major_frame_length, sense=grb.GRB.MINIMIZE)

        self.model = model
        self.x = x_ijk
        self.l = [l_j[j] for j in range(n_win_ub)]


    def solve(self) -> Tuple[instance.Solution, List[instance.Task]]:
        num_tasks = len(self.acs)
        windows_ub = self.n_win_ub
        n_solts = sum([p.processing_units for p in self.env.processors_list])
        model = self.model
        env = self.env

        # OPTIMIZE THE MODEL
        t_start=time.time()
        model.optimize()
        t_end=time.time()

        solution=None
        tasks=[]

        s_feasible=True if model.SolCount > 0 else False
        s_solver_name="ILP global regression"
        s_solution_time=int(round((t_end - t_start)*1000))  # to ms
        s_windows=[]
        s_metadata={"objective": "-1"}

        if s_feasible:
            s_metadata["objective"] = str(model.ObjVal)
            for j in range(windows_ub):
                window_length=int(round(self.l[j].X))
                window_tasks_assignments=[]
                if window_length < 1:
                    continue

                # processor-unit allocation (start with all processors empty)
                pu_allocations={p.name: 0 for p in env.processors_list}

                for i in range(num_tasks):
                    push_task=False
                    task_characteristic=self.acs[i]
                    task_processors=[]
                    task_length=-1
                    task_ass_idx = -1
                    
                    for k, ac in enumerate(task_characteristic.resource_assignmnets):
                        if self.x[i,j,k].X > 0.5:
                            task_ass_idx = k
                            push_task=True                            
                            for p in ac.processors:
                                window_tasks_assignments.append(instance.TaskAssignment(task=task_characteristic.task,
                                                                                        processor=p.processor,
                                                                                        processing_unit=pu_allocations[p.processor],
                                                                                        start=0,
                                                                                        length=ac.length))

                                # increment the processor units
                                pu_allocations[p.processor] += p.processing_units
                                                                
                                task_processors.append(instance.ProcessorAssignment(
                                    p.processor, p.processing_units))
                                task_length=ac.length


                    if push_task:
                        tasks.append(instance.Task(name=task_characteristic.task,
                                                   command=task_characteristic.command,
                                                   length=task_length,
                                                   assignment_index=task_ass_idx,
                                                   processors=task_processors))                    
            
                s_windows.append(instance.Window(window_length, window_tasks_assignments))
        else:  # infeasible solution            
            s_feasible=False
            self.model.computeIIS()
            self.model.write("iis.ilp")
    
        solution = instance.Solution(s_feasible, s_solver_name, s_solution_time, s_metadata, s_windows)
        
        return (solution, tasks)

