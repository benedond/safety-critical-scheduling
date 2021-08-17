#! /usr/bin/python3
from common import arg_parser as ap
from common import instance
from typing import List, Tuple, Mapping
import gurobipy as grb
import sys
import time


class Solver:

    def __init__(self, arg_parser: ap.ArgParser, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], assignment: Mapping[str, int], timelimit:float=float("inf"), cutoff=None):
        self.arg_parser = arg_parser
        self.env = env
        self.acs = acs        
        self.assignment = assignment
        self.timelimit = timelimit
        self.cutoff=cutoff
        self.model = None
        self.x_ij = None
        self.l_j = None
        idx_to_task = {i: x.task for i,x in enumerate(self.acs)}
        self.idx_to_ass = {idx: self.assignment[idx_to_task[idx]] for idx in range(len(self.acs))}
        
        self._init()
        
    def _init(self):
        num_tasks = len(self.acs)
        windows_ub = num_tasks
        env = self.env        
        idx_to_ass = self.idx_to_ass

        model = grb.Model()
        model.setParam("TimeLimit", self.timelimit)
        if self.cutoff:
            model.setParam("Cutoff", self.cutoff)
        # VARIABLES
        # x_ij variables        
        x_ij = model.addVars(num_tasks, windows_ub, vtype=grb.GRB.BINARY, name="x")        

        # l_j variables
        l_j = model.addVars(windows_ub, vtype=grb.GRB.INTEGER, name="l")

        # B_j variables to linearize max b_ijk
        B_j = model.addVars(windows_ub, vtype=grb.GRB.CONTINUOUS, lb=0, name="B")

        # CONSTRAINTS
        # - assignment constraint
        model.addConstrs(x_ij.sum(i, "*") == 1 for i in range(num_tasks))
        
        # - window length constraint - batching
        model.addConstrs(l_j[j] >= ((x_ij[i, j] * self.acs[i].resource_assignmnets[idx_to_ass[i]].length) / env.sc_part)
                         for i in range(num_tasks)
                         for j in range(windows_ub))

        # - window length constraint - if nothing is assigned, window is empty                                
        model.addConstrs((l_j[j] <= env.major_frame_length * x_ij.sum("*", j)
                          for j in range(windows_ub)), name="window is not empty")

        # - major length constraint
        model.addConstr(l_j.sum("*") <= env.major_frame_length,
                        name="major frame length")

        # - resource capacity constraint
        model.addConstrs((grb.quicksum(x_ij[i, j] * acp.processing_units
                                       for i in range(num_tasks)                                       
                                       for acp in self.acs[i].resource_assignmnets[idx_to_ass[i]].processors if acp.processor == processor.name)
                          <= processor.processing_units
                         for processor in env.processors_list
                         for j in range(windows_ub)), name="resource capacity")

        # - link B_j with  b_ik coefficients        
        M = env.major_frame_length * max([self.acs[i].resource_assignmnets[k].intercept
                                            for i in range(num_tasks)
                                            for k in range(len(self.acs[i].resource_assignmnets))])
        model.addConstrs((B_j[j] >= env.sc_part * l_j[j] * self.acs[i].resource_assignmnets[idx_to_ass[i]].intercept - M * (1-x_ij[i, j])
                          for i in range(num_tasks)
                          for j in range(windows_ub)), name="B_j value link")        

        # OBJECTIVE
        energy_consumption_sum=grb.quicksum(B_j[j] + grb.quicksum(x_ij[i, j]
                                                                  * self.acs[i].resource_assignmnets[idx_to_ass[i]].length
                                                                  * self.acs[i].resource_assignmnets[idx_to_ass[i]].slope
                                                                  for i in range(num_tasks))
                                            for j in range(windows_ub))
        model.setObjective(energy_consumption_sum * 1/env.major_frame_length, sense=grb.GRB.MINIMIZE)
        
            
        self.model = model
        self.x_ij = x_ij
        self.l_j = l_j

    def solve(self) -> Tuple[instance.Solution, List[instance.Task]]:
        num_tasks = len(self.acs)
        windows_ub = num_tasks
        env = self.env
        model = self.model
        x_ij = self.x_ij
        l_j = self.l_j

        # OPTIMIZE THE MODEL
        t_start=time.time()
        model.optimize()
        t_end=time.time()

        solution=None
        tasks=[]

        s_feasible=True if model.Status == grb.GRB.OPTIMAL or (
            model.Status == grb.GRB.TIME_LIMIT and model.SolCount > 0) else False
        s_solver_name="ILP-fixed"
        s_solution_time=int(round((t_end - t_start)*1000))  # to ms
        s_windows=[]
        s_metadata={"objective": "-1"}

        if s_feasible:
            s_metadata["objective"] = str(model.ObjVal)
            for j in range(windows_ub):
                window_length=int(round(l_j[j].X))
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

                    k = self.idx_to_ass[i]
                    ac = task_characteristic.resource_assignmnets[k]
                    
                    if x_ij[i, j].X > 0.5:                        
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
                                                   assignment_index=k,
                                                   processors=task_processors))
            
                s_windows.append(instance.Window(window_length, window_tasks_assignments))
        else:  # infeasible solution            
            s_feasible=False
            if self.arg_parser.is_arg_present("--iis-output"):
                model.computeIIS()
                model.write(self.arg_parser.get_arg_value("--iis-output") + ".ilp")        
        solution = instance.Solution(s_feasible, s_solver_name, s_solution_time, s_metadata, s_windows)
        
        return (solution, tasks)
