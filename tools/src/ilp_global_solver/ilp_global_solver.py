#! /usr/bin/python3
from common import arg_parser as ap
from common import instance
from typing import List, Tuple
import gurobipy as grb
import sys
import time


class Solver:

    def __init__(self, arg_parser: ap.ArgParser, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], timelimit:float=float("inf")):
        self.arg_parser = arg_parser
        self.env = env
        self.acs = acs        
        self.timelimit = timelimit
        self.model = None
        self.x_ijk = None
        self.l_j = None
        
        self._init()
        
    def _init(self):
        num_tasks = len(self.acs)
        windows_ub = num_tasks
        env = self.env

        model = grb.Model()
        model.setParam("TimeLimit", self.timelimit)

        # VARIABLES
        # x_ijk variables        
        x_ijk = model.addVars([(i, j, k)
                               for i in range(num_tasks)
                               for j in range(windows_ub)
                               for k in range(len(self.acs[i].resource_assignmnets))],
                              vtype=grb.GRB.BINARY,
                              name="x")        

        # l_j variables
        l_j = model.addVars(windows_ub, vtype=grb.GRB.INTEGER, name="l")

        # B_j variables to linearize max b_ijk
        B_j = model.addVars(windows_ub, vtype=grb.GRB.CONTINUOUS, lb=0, name="B")

        # CONSTRAINTS
        # - assignment constraint
        model.addConstrs(x_ijk.sum(i, "*", "*") == 1
                         for i in range(num_tasks))
        
        # - window length constraint - batching
        model.addConstrs(l_j[j] >= ((x_ijk[i, j, k] * self.acs[i].resource_assignmnets[k].length) / env.sc_part)
                         for i in range(num_tasks)
                         for j in range(windows_ub)
                         for k in range(len(self.acs[i].resource_assignmnets)))

        # - window length constraint - if nothing is assigned, window is empty                                
        model.addConstrs((l_j[j] <= env.major_frame_length * x_ijk.sum("*", j, "*")
                          for j in range(windows_ub)), name="window is not empty")

        # - window ordering constraint (symmetry pruning)
        #model.addConstrs((l_j[j] <= l_j[j-1]
        #                 for j in range(1, windows_ub)), name="window ordering")

        # - major length constraint
        model.addConstr(l_j.sum("*") <= env.major_frame_length,
                        name="major frame length")

        # - resource capacity constraint
        model.addConstrs((grb.quicksum(x_ijk[i, j, k] * acp.processing_units
                                       for i in range(num_tasks)
                                       for k in range(len(self.acs[i].resource_assignmnets))
                                       for acp in self.acs[i].resource_assignmnets[k].processors if acp.processor == processor.name)
                          <= processor.processing_units
                         for processor in env.processors_list
                         for j in range(windows_ub)), name="resource capacity")

        # - link B_j with  b_ik coefficients        
        M = env.major_frame_length * max([self.acs[i].resource_assignmnets[k].intercept
                                            for i in range(num_tasks)
                                            for k in range(len(self.acs[i].resource_assignmnets))])
        model.addConstrs((B_j[j] >= env.sc_part * l_j[j] * self.acs[i].resource_assignmnets[k].intercept - M * (1-x_ijk[i, j, k])
                          for i in range(num_tasks)
                          for j in range(windows_ub)
                          for k in range(len(self.acs[i].resource_assignmnets))), name="B_j value link")

        # OBJECTIVE
        energy_consumption_sum=grb.quicksum(B_j[j] + grb.quicksum(x_ijk[i, j, k]
                                                                  * self.acs[i].resource_assignmnets[k].length
                                                                  * self.acs[i].resource_assignmnets[k].slope
                                                                  for i in range(num_tasks)
                                                                  for k in range(len(self.acs[i].resource_assignmnets)))
                                            for j in range(windows_ub))
        model.setObjectiveN(energy_consumption_sum * 1/env.major_frame_length,
                            index=0, priority=1, weight=1.0, name="min avg power consumption");

        if (self.arg_parser.is_arg_present("--optimize-schedule")):
            print("warning: --optimize-schedule active with predictor method", file=sys.stderr)
            model.setObjectiveN(l_j.sum("*"),
                                index=1, priority=0, weight=1.0, name="min total schedule length")
            
        self.model = model
        self.x_ijk = x_ijk
        self.l_j = l_j

    def solve(self) -> Tuple[instance.Solution, List[instance.Task]]:
        num_tasks = len(self.acs)
        windows_ub = num_tasks
        env = self.env
        model = self.model
        x_ijk = self.x_ijk
        l_j = self.l_j

        # OPTIMIZE THE MODEL
        t_start=time.time()
        model.optimize()
        t_end=time.time()

        solution=None
        tasks=[]

        s_feasible=True if model.Status == grb.GRB.OPTIMAL or (
            model.Status == grb.GRB.TIME_LIMIT and model.SolCount > 0) else False
        s_solver_name="ILP Solver (global):predictor (Python)"
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

                    for k, ac in enumerate(task_characteristic.resource_assignmnets):
                        if x_ijk[i, j, k].X > 0.5:
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
            if self.arg_parser.is_arg_present("--iis-output"):
                model.computeIIS()
                model.write(self.arg_parser.get_arg_value("--iis-output") + ".ilp")        
        solution = instance.Solution(s_feasible, s_solver_name, s_solution_time, s_metadata, s_windows)
        
        return (solution, tasks)
