import nevergrad as ng
import numpy as np
from common import arg_parser as ap
from common import instance
from typing import List, Tuple
import sys
import time


class Solver:

    def __init__(self, arg_parser: ap.ArgParser, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], timelimit:float=float("inf"), budget:int=100):
        self.arg_parser = arg_parser
        self.env = env
        self.acs = acs       
        self.budget = budget 
        self.timelimit = timelimit
        self.parametrization = None        
        self.optimizer = None
        self.recommendation = None
        
        self.slots_per_window = sum([p.processing_units for p in env.processors_list])
        
        self.slot_to_proc = {}
        offset = 0
        for idx, p in enumerate(self.env.processors_list):
            for u in range(p.processing_units):
                self.slot_to_proc[u+offset] = idx
                
            offset += p.processing_units
                    
        self.obj_ub = (env.major_frame_length * (1+sum(p.processing_units for p in env.processors_list))
        * max([ max(r.slope, r.intercept) for a in acs for r in a.resource_assignmnets]))
        
        self._init()
        
    def _init(self):
        n_tasks = len(self.acs)
        windows_ub = n_tasks        
        env = self.env
        
        number_of_allowed_ra = 2

        # Check that every task has exactly two allocations
        for ac in self.acs:
            assert len(ac.resource_assignmnets) == number_of_allowed_ra, "Nevergrad solver assumes that each task has two assignments -> to little and big cluster, respectively."

        # Compute the number of all slots -> first n correspond to the tasks, rest are just idle (empty) slots
        number_of_slots = windows_ub  * self.slots_per_window
        
        #init = np.concatenate((np.random.rand(n_tasks), np.ones(number_of_slots - n_tasks)))
        
        parametrization = ng.p.Instrumentation(
            order = ng.p.Array(shape=(number_of_slots,), lower=0.0, upper=1.0)
        )
                
        #optimizer = ng.optimizers.PSO(parametrization=parametrization, budget=self.budget)
        optimizer = ng.optimizers.NGOpt(parametrization=parametrization, budget=self.budget)
                        
        # Set time limit
        optimizer.register_callback("ask", ng.callbacks.EarlyStopping.timer(self.timelimit))                
        
        self.parametrization = parametrization
        self.optimizer = optimizer        
        
    
    def get_window_lengths(self, order):
        n_tasks = len(self.acs)
        n_win = n_tasks        
                        
        w_len = np.zeros(n_win)
        
        indexes = np.argsort(order)        
        
        for w in range(n_win):
            for s in range(self.slots_per_window):
                cur_idx = w*self.slots_per_window + s
                cur_task = indexes[cur_idx]
                
                if cur_task >= n_tasks:  # dummy idle
                    continue
                
                ra = self.acs[cur_task].resource_assignmnets[self.slot_to_proc[s]]
                
                w_len[w] = max(w_len[w], ra.length)
        
        return w_len                                         

    def fitness(self, order):  
        #print(order)       
        n_tasks = len(self.acs)
        n_win = n_tasks        
                        
        w_len = self.get_window_lengths(order)
        sum_dynamic = np.zeros(n_win)
        max_static = np.zeros(n_win)
                       
        indexes = np.argsort(order)
                
        
        for w in range(n_win):
            for s in range(self.slots_per_window):
                cur_idx = w*self.slots_per_window + s
                cur_task = indexes[cur_idx]
                
                if cur_task >= n_tasks:  # dummy idle
                    continue
                
                ra = self.acs[cur_task].resource_assignmnets[self.slot_to_proc[s]]
                sum_dynamic[w] += ra.slope * ra.length
                max_static[w] = max(max_static[w], ra.intercept)                
        
        obj = np.sum(sum_dynamic + (max_static * w_len)) / self.env.major_frame_length                   
        
        if np.sum(w_len) > self.env.major_frame_length:
            return self.obj_ub + obj
        else:
            return obj

    def get_task_allocations(self, order):
        n_win = n_tasks = len(self.acs)
        indexes = np.argsort(order)
        allocations = [0 for _ in range(n_tasks)]
        
        for w in range(n_win):
            for s in range(self.slots_per_window):
                cur_idx = w*self.slots_per_window + s
                cur_task = indexes[cur_idx]
                
                if cur_task >= n_tasks:  # dummy idle
                    continue
                
                allocations[cur_task] = (w, self.slot_to_proc[s])
                
        return allocations

    def solve(self) -> Tuple[instance.Solution, List[instance.Task]]:                
        num_tasks = len(self.acs)
        windows_ub = num_tasks
        env = self.env
        optimizer = self.optimizer 

        # OPTIMIZE THE MODEL
        t_start=time.time()           
        #recommendation = optimizer.minimize(Solver.static_fitness, verbosity=1)        
        recommendation = optimizer.minimize(self.fitness, verbosity=1)        
        t_end=time.time()

        order = recommendation.kwargs["order"]
        allocation = self.get_task_allocations(order)
        
        # Get the solution
        solution=None
        tasks=[]

        s_feasible=True if allocation else False
        s_solver_name="nevergrad"
        s_solution_time=int(round((t_end - t_start)*1000))  # to ms
        s_windows=[]
        s_metadata={"objective": str(float("inf"))}

        if s_feasible:
            s_metadata["objective"] = str(self.fitness(order))
            w_lengths = self.get_window_lengths(order)
            
            for j in range(windows_ub):                
                window_length=w_lengths[j]
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
                        if allocation[i] == (j,k):                        
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
