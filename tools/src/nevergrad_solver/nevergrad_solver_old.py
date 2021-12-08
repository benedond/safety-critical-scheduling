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
        
        self._init()
        
    def _init(self):
        n_tasks = len(self.acs)
        windows_ub = n_tasks
        env = self.env
        
        number_of_allowed_ra = 2

        # Check that every task has exactly two allocations
        for ac in self.acs:
            assert len(ac.resource_assignmnets) == number_of_allowed_ra, "Nevergrad solver assumes that each task has two assignments -> to little and big cluster, respectively."

        # Prepare all possible allocations
        allocations = [(w,a) for w in range(windows_ub) for a in range(number_of_allowed_ra)]

        parametrization = ng.p.Instrumentation(
            allocation = ng.p.Choice(allocations, repetitions=n_tasks)
        )
                
        # optimizer = ng.optimizers.NGOpt(parametrization=parametrization, budget=self.budget)
        optimizer = ng.optimizers.PortfolioDiscreteOnePlusOne(parametrization=parametrization, budget=self.budget)
        
                        
        # Set time limit
        optimizer.register_callback("ask", ng.callbacks.EarlyStopping.timer(self.timelimit))
        
        # Add constraint: check if the assignment is feasible
        optimizer.parametrization.register_cheap_constraint(lambda x: self.is_feasible(x[1]["allocation"]))                          
        
        self.parametrization = parametrization
        self.optimizer = optimizer        
        
    
    def get_window_lengths(self, allocation):
        n_tasks = len(allocation)
        n_win = n_tasks
                        
        w_len = np.zeros(n_win)
                    
        for idx, a in enumerate(allocation):
            a_window = a[0]
            a_conf_id = a[1]
            
            ra = self.acs[idx].resource_assignmnets[a_conf_id]
            w_len[a_window] = max(w_len[a_window], ra.length)            

        return w_len    
            
    def is_feasible(self, allocation):
        n_tasks = len(allocation)
        n_win = n_tasks
                
        n_tasks_on_proc = {p.name: np.zeros(n_win) for p in self.env.processors_list}
        w_len = np.zeros(n_win)
                    
        for idx, a in enumerate(allocation):
            a_window = a[0]
            a_conf_id = a[1]
            
            ra = self.acs[idx].resource_assignmnets[a_conf_id]
            w_len[a_window] = max(w_len[a_window], ra.length)
            for proc_assignment in ra.processors:
                n_tasks_on_proc[proc_assignment.processor][a_window] += proc_assignment.processing_units

        # Check the major frame length
        if np.sum(w_len) > self.env.major_frame_length:
            return False

        # Check that allocation does not overuse processors capacity                
        for p_name, n_tasks in n_tasks_on_proc.items():
            if not np.all(n_tasks <= self.env.processors[p_name].processing_units):
                return False
        
        return True


    def fitness(self, allocation):         
        n_tasks = len(allocation)
        n_win = n_tasks
        
        if not self.is_feasible(allocation):
            return float("inf")
        
        sum_dynamic = np.zeros(n_win)
        max_static = np.zeros(n_win)
        w_len = self.get_window_lengths(allocation)
                    
        for idx, a in enumerate(allocation):
            a_window = a[0]
            a_conf_id = a[1]
            
            ra = self.acs[idx].resource_assignmnets[a_conf_id]
            sum_dynamic[a_window] += ra.slope * ra.length
            max_static[a_window] = max(max_static[a_window], ra.intercept)

        return np.sum(sum_dynamic + (max_static * w_len)) / self.env.major_frame_length
            

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

        allocation = recommendation.kwargs["allocation"]

        # Get the solution
        solution=None
        tasks=[]

        s_feasible=True if allocation else False
        s_solver_name="nevergrad"
        s_solution_time=int(round((t_end - t_start)*1000))  # to ms
        s_windows=[]
        s_metadata={"objective": str(float("inf"))}

        if s_feasible:
            s_metadata["objective"] = self.fitness(allocation)
            w_lengths = self.get_window_lengths(allocation)
            
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
