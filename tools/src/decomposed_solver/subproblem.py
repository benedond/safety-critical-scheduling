# Subproblem - polynomial solver
import numpy as np
from typing import List

def solve(pi_i: np.array):
    pass

    for l in possible_lengths:
        for task_l in possible_lengths[l]:
            # fix task_l
            
            # filter remaining tasks < l
            
            # filter by resource capacity
            
            # add fix_l to filtered tasks
            for b in possible_b:
                for task_b in possible_b[b]:
                    # fix task_b if task_b not task_l
                    
                    # filter remaining tasks < b (and < l)
                    
                    # filter by resource capacity
                    
                    # sort the remaining tasks-assignments according to pi_i and a
                    
                    for cur_task in remaining_tasks:
                        if not scheduled[cur_task]:
                            if not enough capacity to schedule cur_task:
                                continue
                            else:
                                # fix selected assignment of cur_task
                            