import nevergrad as ng
import numpy as np
import json

                                 

def fitness(order):  
    w_len = np.zeros(n_win_ub)
    sum_dynamic = np.zeros(n_win_ub)
    max_static = np.zeros(n_win_ub)
                    
    indexes = np.argsort(order)
            
    
    for w in range(n_win_ub):
        for s in range(slots_per_window):
            cur_idx = w*slots_per_window + s
            cur_task = indexes[cur_idx]
            
            if cur_task >= n_tasks:  # dummy idle
                continue
            
            ra = tasks_char[str(slot_to_proc[s])][str(cur_task + 1)]
            sum_dynamic[w] += ra["slope"] * ra["length"]
            max_static[w] = max(max_static[w], ra["intercept"])
            w_len[w] = max(w_len[w], ra["length"])                
    
    obj = np.sum(sum_dynamic + (max_static * w_len))                  

    return obj

def run():     
    parametrization = ng.p.Instrumentation(
        order = ng.p.Array(shape=(number_of_slots,), lower=0.0, upper=1.0)
    )
            
    optimizer = ng.optimizers.NGOpt(parametrization=parametrization, budget=1e6)
                    
    # Set time limit
    optimizer.register_callback("ask", ng.callbacks.EarlyStopping.timer(10))                

    recommendation = optimizer.minimize(fitness, verbosity=0)     
    order = recommendation.kwargs["order"]
    print(i, fitness(order))


tasks_char = json.load(open("data.json","r"))
slot_to_proc = {0: 1, 1: 1, 2: 1, 3: 1, 4: 2, 5: 2}
n_tasks = 100
n_win_ub = n_tasks
n_cores = 2
cores = [4, 2]
slots_per_window = sum(cores)

number_of_slots = n_win_ub  * slots_per_window

print("Optimizing by Nevergrad.")
for i in range(10):
    run()