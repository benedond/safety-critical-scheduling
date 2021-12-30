#! /usr/bin/python3
from common import arg_parser as ap
from common import instance
from typing import List, Tuple
import gurobipy as grb
import sys
import time
import numpy as np



def is_feasible(tasks_assignment, env, acs, timelimit=float("inf")):
    n_tasks = len(acs)
    n_win_ub = n_tasks

    model = grb.Model()
    model.setParam("TimeLimit", timelimit)

    
    # VARIABLES
    # x_ijk variables        
    x_ijk = model.addVars([(i, j, k)
                            for i in range(n_tasks)
                            for j in range(n_win_ub)
                            for k in range(len(acs[i].resource_assignmnets))],
                            vtype=grb.GRB.BINARY,
                            name="x")        

    # length of slot in window
    l_j = model.addVars(range(n_win_ub), vtype=grb.GRB.CONTINUOUS, name="l")
    
    # CONSTRAINTS
    # - each task assigned to one of the slots
    model.addConstrs(x_ijk.sum(i, "*", "*") == 1 
        for i in range(n_tasks))

    # get length of each window (ub)
    model.addConstrs(l_j[j] >= x_ijk[i,j,k] * acs[i].resource_assignmnets[k].length
        for i in range(n_tasks) for j in range(n_win_ub) for k in range(len(acs[i].resource_assignmnets)))

    
    # respect capacity of each cluster
    model.addConstrs( grb.quicksum(x_ijk[i,j,k] * p.processing_units for i in range(n_tasks) for k in range(len(acs[i].resource_assignmnets)) for p in acs[i].resource_assignmnets[k].processors if env.processors_list[r_id].name == p.processor) <= env.processors_list[r_id].processing_units
        for j in range(n_win_ub) for r_id in range(len(env.processors_list))
    )

    # respect the major frame length
    model.addConstr(grb.quicksum(l_j[j] for j in range(n_win_ub)) <= env.major_frame_length)

    # - window ordering constraint (symmetry pruning)
    model.addConstrs((l_j[j] >= l_j[j+1] for j in range(n_win_ub-1)))

    # fix assignment
    for t_idx, ac_idx in tasks_assignment.items():
        model.addConstr(x_ijk.sum(t_idx, "*", ac_idx) == 1)

    # solve model
    model.optimize()

    if model.SolCount == 0:
        return []
    else:
        task_to_win_and_ac = [None for _ in range(n_tasks)]

        for i in range(n_tasks):
            for j in range(n_win_ub):
                for k in range(len(acs[i].resource_assignmnets)):
                    if x_ijk[i,j,k].X > 0.5:
                        task_to_win_and_ac[i] = (j,k)

        return task_to_win_and_ac


class Solver:
    def __init__(self, arg_parser: ap.ArgParser, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], minimize=True, timelimit=float("inf")):
        self.arg_parser = arg_parser
        self.env = env
        self.acs = acs
        self.n_win_ub = len(acs)
        self.timelimit = timelimit

    def solve(self) -> Tuple[instance.Solution, List[instance.Task]]:
        t_start = time.time()
        # sort tasks by max slope * proc (dynamic power consumption)
        max_coef = [ max([ra.slope * ra.length for ra in self.acs[i].resource_assignmnets]) for i in range(len(self.acs))]
        tasks_idx_order = sorted(range(len(self.acs)), key=lambda x: max_coef[x], reverse=True)
        
        task_assignment = dict()  # task_idx => acs idx

        for task_idx in tasks_idx_order:
            ac = self.acs[task_idx]
            assigned = False

            ac_coef = [ra.slope * ra.length for ra in ac.resource_assignmnets]
            ra_idx_order = sorted(range(len(ac_coef)), key=lambda x: ac_coef[x])

            for ra_idx in ra_idx_order:
                ra = ac.resource_assignmnets[ra_idx]
                task_assignment[task_idx] = ra_idx
                
                timelimit = max(0, self.timelimit - (time.time() - t_start))
                if timelimit == 0:
                    break
                
                if is_feasible(task_assignment, self.env, self.acs, timelimit):
                    assigned = True
                    break
                else:  # try next assignment
                    task_assignment.pop(task_idx)
                    continue

            if not assigned:
                break
        
        t_end = time.time()
        ##########################################################################
        
        # get solution
        solution=None
        tasks=[]
        s_feasible=True if len(task_assignment.keys()) == len(self.acs) else False
        s_solver_name="HEUR"
        s_solution_time=int(round((t_end - t_start)*1000))  # to ms
        s_windows=[]
        s_metadata={"objective": "-1"}
        
        if s_feasible:
            s_metadata["objective"] = str(0)

            task_to_win_and_ac = is_feasible(task_assignment, self.env, self.acs)
            windows_ub = len(set([x[0] for x in task_to_win_and_ac]))

            for j in range(windows_ub):
                window_length = max([self.acs[idx].resource_assignmnets[x[1]].length for idx, x in enumerate(task_to_win_and_ac) if x[0] == j])
                window_tasks_assignments=[]
                if window_length < 1:
                    continue

                # processor-unit allocation (start with all processors empty)
                pu_allocations={p.name: 0 for p in self.env.processors_list}

                for i in range(len(task_to_win_and_ac)):
                    if task_to_win_and_ac[i][0] != j:  # task i is not in window j
                        continue

                    task_characteristic=self.acs[i]
                    task_processors=[]
                    task_ass_idx = task_to_win_and_ac[i][1]
                    ac = self.acs[i].resource_assignmnets[task_ass_idx]
                    
                    task_length = ac.length
                    
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