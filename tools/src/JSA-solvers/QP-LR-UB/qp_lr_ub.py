#! /usr/bin/python3
from common import arg_parser as ap
from common import instance
from typing import List, Tuple
import gurobipy as grb
import sys
import time
import numpy as np
import logging


def get_coeff(which: str, res: str, lr_coeffs):
    return lr_coeffs[res][which]

class Solver:
    def __init__(self, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], lr_coeffs: dict, timelimit=float("inf")):
        self.env = env
        self.acs = acs
        self.timelimit = timelimit
        self.lr_coeffs = lr_coeffs
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
        model.setParam("TimeLimit", self.timelimit)


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
            l_j[j] * grb.quicksum(x_ijk[i,j,k] * (self.acs[i].resource_assignmnets[k].slope * get_coeff("slope", self.acs[i].resource_assignmnets[k].processors[0].processor, self.lr_coeffs) + self.acs[i].resource_assignmnets[k].intercept * get_coeff("intercept", self.acs[i].resource_assignmnets[k].processors[0].processor, self.lr_coeffs))
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
        s_solver_name="QP-LR-UB"
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
                
                if len(window_tasks_assignments) > 0:
                    s_windows.append(instance.Window(window_length, window_tasks_assignments))
        else:  # infeasible solution            
            s_feasible=False
            self.model.computeIIS()
            self.model.write("iis.ilp")
    
        solution = instance.Solution(s_feasible, s_solver_name, s_solution_time, s_metadata, s_windows)
        
        return (solution, tasks)

