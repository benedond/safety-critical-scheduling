import nevergrad as ng
import numpy as np



cores = [4,2] 

task_proc_A53 = [2,5,3,4,5]
task_proc_A72 = [1,3,2,4,6]
n_tasks = 5
major_frame_length = 8

allocations = [(w,0) for w in range(n_tasks)] + [(w,1) for w in range(n_tasks)]


def is_sorted(a):
    for i in range(a.size-1):
         if a[i+1] < a[i] :
               return False
    return True

def eval_func(allocation):
    # makespan
    return sum(max([0] + [task_proc_A53[idx] for idx,a in enumerate(allocation) if a[0] == w and a[1] == 0] + [task_proc_A72[idx] for idx,a in enumerate(allocation) if a[0] == w and a[1] == 1] ) for w in range(n_tasks))

def is_feasible(allocation):
    n_tasks = len(allocation)
    n_A53 = np.zeros(n_tasks)
    n_A72 = np.zeros(n_tasks)
    w_len = np.zeros(n_tasks)
    
    for idx, a in enumerate(allocation):
        if a[1] == 0:
            n_A53[a[0]] += 1
            w_len[a[0]] = max(task_proc_A53[idx], w_len[a[0]])
        elif a[1] == 1:
            n_A72[a[0]] += 1
            w_len[a[0]] = max(task_proc_A72[idx], w_len[a[0]])
    
    return np.all(n_A53 <= 4) and np.all(n_A72 <= 2) and np.sum(w_len) <= major_frame_length

parametrization = ng.p.Instrumentation(
    allocation = ng.p.Choice(allocations, repetitions=n_tasks)
)

optimizer = ng.optimizers.NGOpt(parametrization=parametrization, budget=100)
optimizer.register_callback("ask", ng.callbacks.EarlyStopping.timer(1))

optimizer.parametrization.register_cheap_constraint(lambda x: is_feasible(x[1]["allocation"]))
# # For each window
# for i in range(n_tasks):
#     # For each core - respect the capacity    
#     optimizer.parametrization.register_cheap_constraint(lambda x: sum([1 for a in x[1]["allocation"] if a[0] == i and a[1] == 0]) <= 4)
#     optimizer.parametrization.register_cheap_constraint(lambda x: sum([1 for a in x[1]["allocation"] if a[0] == i and a[1] == 1]) <= 2)
    
# # Respect the major frame
# optimizer.parametrization.register_cheap_constraint(lambda x: 
#     sum(max([0] + [task_proc_A53[idx] for idx,a in enumerate(x[1]["allocation"]) if a[0] == w and a[1] == 0] + [task_proc_A72[idx] for idx,a in enumerate(x[1]["allocation"]) if a[0] == w and a[1] == 1]) 
#         for w in range(n_tasks)) <= major_frame_length
#     )


recommendation = optimizer.minimize(eval_func, verbosity=1)

print(recommendation.kwargs)  # shows the recommended keyword arguments of the function
sol = recommendation.kwargs["allocation"]
print(is_feasible(sol))
