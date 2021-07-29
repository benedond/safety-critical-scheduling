import instance
from typing import List, Tuple, Mapping
import time
import gurobipy as grb

class ILPSolver:    
    def __init__(self):
        self.model = None
        self.solved = False
        self.feasible = False
        self.solving_time = None
        self.init_time = None  
        
    def _init_model(self):
        raise NotImplementedError
    
    def solve(self):            
        t_start=time.time()
        self.model.optimize()
        t_end=time.time()
        
        s_feasible=True if self.model.Status == grb.GRB.OPTIMAL or (
            self.model.Status == grb.GRB.TIME_LIMIT and self.model.SolCount > 0) else False
        
        self.solved = True
        self.feasible = s_feasible   
        self.solving_time = t_end - t_start


class MasterModel(ILPSolver):
    def __init__(self, patterns: List[instance.Pattern], major_frame_length: int, tasks: List[str], bin_vars: bool=False):
        self.alpha = None
        self.patterns = patterns
        self.major_frame_length = major_frame_length
        self.tasks = tasks
        self.c0 = None
        self.ct = {}        
        self.bin_vars = bin_vars
        
        t_s = time.time()
        self._init_model()
        t_e = time.time()
        self.init_time = t_e - t_s
        
    def _init_model(self):
        m = grb.Model("Master Model")
        
        # variables
        if self.bin_vars:
            alpha = m.addVars(len(self.patterns), vtype=grb.GRB.BINARY, lb=0, ub=1, name="alpha")
        else:
            alpha = m.addVars(len(self.patterns), vtype=grb.GRB.CONTINUOUS, lb=0, ub=1, name="alpha")
        
        
        # constraints
        # - major frame length        
        self.c0 = m.addConstr(grb.quicksum(alpha[i] * p.length for i, p in enumerate(self.patterns)) <= self.major_frame_length, name="C:major_frame")
        
        # - patterns cover tasks
        for t in self.tasks:                        
            self.ct[t] = m.addConstr(grb.quicksum(alpha[i] for i, p in enumerate(self.patterns) if t in p.task_mapping) >= 1, 
                                                  name="C:task_cover_{}".format(t))  # TODO: should be >= 1 or == 1 ? 
        
        # objective
        m.setObjective(grb.quicksum(alpha[i] * p.cost for i, p in enumerate(self.patterns)), sense=grb.GRB.MINIMIZE)
        
        self.model = m
        self.alpha = alpha
        
    def is_solution_integer(self) -> bool:
        EPS = 1e-4
        for i in range(len(self.alpha)):
            if EPS < self.alpha[i].X < 1 - EPS:
                return False
        return True        
    
    def get_objective(self) -> float:
        if self.feasible:
            return self.model.objVal * (1/self.major_frame_length)
        else:
            return None

                     
    def get_dual_prices(self) -> Tuple[float, Mapping[str, float]]:
        if not self.solved:
            logging.warning("get_dual_prices cannot be called for unsolved model; call solve() first")            
        if not self.feasible:
            logging.warning("model is not feasible, dual prices cannot be obtained")
        return self.c0.Pi, {t: self.ct[t].Pi for t in self.tasks}
    
    def get_solution(self):
        sol = []
        for i, p in enumerate(self.patterns):
            if self.alpha[i].X > 0:  # TODO: comparison
                sol.append({"index": i, "value": self.alpha[i].X})
                
        return sol
    
    def get_selected_patterns(self) -> List[instance.Pattern]:        
        EPS = 1e-4
        return [self.patterns[i] for i in range(len(self.alpha)) if self.alpha[i].X > EPS]
    
    def get_solution_and_tasks(self, env: instance.Environment, acs:  List[instance.AssignmentCharacteristic]):                            
        solution=None
        tasks=[]        

        s_feasible=True if self.model.Status == grb.GRB.OPTIMAL or (
            model.Status == grb.GRB.TIME_LIMIT and model.SolCount > 0) else False
        s_solver_name="BAP"
        s_solution_time=int(round(self.solving_time*1000))  # to ms
        s_windows=[]
        s_metadata={"objective": "-1"}

        if s_feasible:
            s_metadata["objective"] = str(self.model.ObjVal / self.major_frame_length) 
            
            for j, p in enumerate(self.patterns):
                if self.alpha[j].X > 0:  # TODO: comparison
                    window_length = p.length
                    window_tasks_assignments=[]
                    
                    if window_length < 1:
                        continue
                                                    
                    # processor-unit allocation (start with all processors empty)
                    pu_allocations={p.name: 0 for p in env.processors_list}
                                    
                    for t in p.task_mapping:
                        ac = [a for a in acs if a.task == t][0]  # assignment characteristic of the current task
                        cur_ra = ac.resource_assignmnets[p.task_mapping[t]]
                        task_processors = []
                        for pr in cur_ra.processors:  
                            window_tasks_assignments.append(instance.TaskAssignment(task=t,
                                                                                    processor=pr.processor,
                                                                                    processing_unit=pu_allocations[pr.processor],
                                                                                    start=0,
                                                                                    length=cur_ra.length))
                            
                                                        
                            # increment the processor units
                            pu_allocations[pr.processor] += pr.processing_units                                
                            task_processors.append(instance.ProcessorAssignment(pr.processor, pr.processing_units))                                 
                                    
                        tasks.append(instance.Task(name=t,
                                                command=ac.command,
                                                length=cur_ra.length,
                                                assignment_index=p.task_mapping[t],
                                                processors=task_processors))                    
                
                    s_windows.append(instance.Window(window_length, window_tasks_assignments))
        else:  # infeasible solution            
            s_feasible=False
            if self.arg_parser.is_arg_present("--iis-output"):
                model.computeIIS()
                model.write(self.arg_parser.get_arg_value("--iis-output") + ".ilp")        
        solution = instance.Solution(s_feasible, s_solver_name, s_solution_time, s_metadata, s_windows)
        
        return (solution, tasks)

class SubproblemModelILP(ILPSolver):
    
    def __init__(self, env: instance.Environment, acs: List[instance.AssignmentCharacteristic], dual_prices: Tuple[float, Mapping[str, float]],
                 on_same: List[Tuple[str,str]], on_diff: List[Tuple[str,str]]):
        self.env = env
        self.acs = acs
        self.dual_prices = dual_prices 
        self.on_same = on_same
        self.on_diff = on_diff
        self.x_ik = None       
        self.l = None        
        
        t_s = time.time()
        self._init_model()        
        t_e = time.time()
        self.init_time = t_e - t_s
        
    def _init_model(self):
        m = grb.Model("Subproblem-ILP")
        num_tasks = len(self.acs)
        
        task_to_idx = {}
        for i, a in enumerate(self.acs):
            task_to_idx[a.task] = i

        # variables
        x_ik = m.addVars([(i, k)
                          for i in range(num_tasks)                               
                          for k in range(len(self.acs[i].resource_assignmnets))],
                          vtype=grb.GRB.BINARY,
                          name="x")        
        l = m.addVar(vtype=grb.GRB.INTEGER, lb=0, name="l")
        B = m.addVar(vtype=grb.GRB.CONTINUOUS, lb=0, name="B")                    
        
        # constraints
        # - B value
        M = self.env.major_frame_length * max([self.acs[i].resource_assignmnets[k].intercept
                                                for i in range(num_tasks)
                                                for k in range(len(self.acs[i].resource_assignmnets))])
        m.addConstrs(B >= l * self.acs[i].resource_assignmnets[k].intercept - M * (1-x_ik[i,k])
                     for i in range(num_tasks)
                     for k in range(len(self.acs[i].resource_assignmnets)))
        
        # - assign task to at most one resource
        m.addConstrs(x_ik.sum(i, "*") <= 1
                    for i in range(num_tasks))
        
        # - respect capacity of the resource        
        m.addConstrs((grb.quicksum(x_ik[i, k] * acp.processing_units
                                       for i in range(num_tasks)
                                       for k in range(len(self.acs[i].resource_assignmnets))
                                       for acp in self.acs[i].resource_assignmnets[k].processors if acp.processor == processor.name)
                          <= processor.processing_units
                          for processor in self.env.processors_list),
                         name="resource capacity")
        
        # - constrain window length
        m.addConstrs(l >= x_ik[i, k] * self.acs[i].resource_assignmnets[k].length
                     for i in range(num_tasks)
                     for k in range(len(self.acs[i].resource_assignmnets)))
        m.addConstr(l <= self.env.major_frame_length)

        # - branching constraints
        for t1, t2 in self.on_same:
            i1 = task_to_idx[t1]
            i2 = task_to_idx[t2]
            m.addConstr(x_ik.sum(i1, "*") == x_ik.sum(i2,"*"))  # in same window
            #m.addConstr(x_ik[i1, k] == x_ik[i2, k] for k in range(len(self.acs[i].resource_assignmnets)))  # in same window

        for t1, t2 in self.on_diff:
            i1 = task_to_idx[t1]
            i2 = task_to_idx[t2]
            m.addConstr(x_ik.sum(i1, "*") + x_ik.sum(i2,"*") <= 1 )  # in different windows
            #m.addConstr(x_ik[i1, k] + x_ik[i2,k] <= 1 for k in range(len(self.acs[i].resource_assignmnets)))  # in different windows
        
        # objective
        obj = grb.quicksum(x_ik[i, k] * (self.acs[i].resource_assignmnets[k].length
                                         * self.acs[i].resource_assignmnets[k].slope 
                                         -  self.dual_prices[1][self.acs[i].task])
                           for i in range(num_tasks)
                           for k in range(len(self.acs[i].resource_assignmnets))) - l*self.dual_prices[0] + B      
        m.setObjective(obj, sense=grb.GRB.MINIMIZE)
        
        self.model = m
        self.x_ik = x_ik
        self.l = l
        
    def get_pattern(self) -> instance.Pattern:
        if not self.solved:
            logging.warning("model was not solved")
            return None
        if not self.feasible:
            logging.warning("model is not feasible")
            return None
        
        p_len = int(round(self.l.X))
        #p_cost = self.model.ObjVal + self.dual_prices[0] * p_len        
        p_task_mapping = {}
        
        for i in range(len(self.acs)):
            for k in range(len(self.acs[i].resource_assignmnets)):
                if self.x_ik[i,k].X > 0.5:
                    p_task_mapping[self.acs[i].task] = k
                    #p_cost += self.dual_prices[1][self.acs[i].task]
                    break

        # recompute the cost manually to avoid potential numerical problems
        pattern = instance.Pattern(0, p_len, p_task_mapping)                
        cost = pattern.compute_cost(self.acs)
        pattern.cost = cost
        
        return pattern
   
    def get_patterns(self) -> List[instance.Pattern]:
        if not self.solved:
            logging.warning("model was not solved")
            return None
        if not self.feasible:
            logging.warning("model is not feasible")
            return None
        
        patterns = []
        
        for sol_idx in range(self.model.SolCount):
            self.model.setParam("SolutionNumber", sol_idx)
            
            if self.model.PoolObjVal < -0.0001:  # TODO: some robust check
        
                p_len = int(round(self.l.Xn))            
                p_task_mapping = {}
            
                for i in range(len(self.acs)):
                    for k in range(len(self.acs[i].resource_assignmnets)):
                        if self.x_ik[i,k].Xn > 0.5:
                            p_task_mapping[self.acs[i].task] = k                        
                            break

                # recompute the cost manually to avoid potential numerical problems
                pattern = instance.Pattern(0, p_len, p_task_mapping)                
                cost = pattern.compute_cost(self.acs)
                pattern.cost = cost

                patterns.append(pattern)
                        
        return patterns            

json_data = instance.read_json_from_file("IN_086.json")
env = instance.parse_environment(json_data)
acs = instance.parse_assignment_characteristics(json_data)    
tasks = [ac.task for ac in acs]

on_same = [('task-8', 'task-12'), ('task-2', 'task-7'), ('task-8', 'task-11')]
on_diff = [('task-1', 'task-7'), ('task-3', 'task-14'), ('task-0', 'task-5'), ('task-4', 'task-13'), ('task-9', 'task-11'), ('task-2', 'task-10'), ('task-8', 'task-6'), ('task-1', 'task-12'), ('task-7', 'task-3'), ('task-14', 'task-0'), ('task-5', 'task-4'), ('task-2', 'task-13'), ('task-11', 'task-10'), ('task-9', 'task-6'), ('task-8', 'task-7'), ('task-1', 'task-3'), ('task-12', 'task-14'), ('task-0', 'task-4'), ('task-5', 'task-2'), ('task-13', 'task-11'), ('task-9', 'task-10'), ('task-1', 'task-6'), ('task-8', 'task-0'), ('task-12', 'task-3'), ('task-14', 'task-5'), ('task-4', 'task-2'), ('task-13', 'task-7'), ('task-11', 'task-6'), ('task-8', 'task-9'), ('task-1', 'task-10'), ('task-12', 'task-5'), ('task-3', 'task-0'), ('task-14', 'task-4'), ('task-13', 'task-9'), ('task-10', 'task-6')]

patterns = [instance.Pattern(6.317972604297501, 5, {'task-5': 1}),
            instance.Pattern(20.74395140529408, 20, {'task-13': 1}),
            instance.Pattern(7.291640564640378, 25, {'task-1': 1}),
            instance.Pattern(48.756073188994, 31, {'task-10': 1}),
            instance.Pattern(57.75767512007975, 65, {'task-14': 1}),
            instance.Pattern(98.57736848803609, 81, {'task-3': 0, 'task-4': 1}),
            instance.Pattern(120.31265074752672, 55, {'task-2': 0, 'task-6': 0, 'task-7': 1}),
            instance.Pattern(57.038926300819575, 47, {'task-0': 1, 'task-9': 0}),
            instance.Pattern(79.04490066083062, 47, {'task-0': 1, 'task-6': 0}),
            instance.Pattern(33.72167903099324, 23, {'task-3': 1}),
            instance.Pattern(7.291640564640378, 25, {'task-1': 1}),
            instance.Pattern(150.85739800348165, 84, {'task-8': 1, 'task-11': 0, 'task-12': 0}),
            instance.Pattern(73.81246095880542, 36, {'task-8': 0, 'task-11': 1, 'task-12': 0}),
            instance.Pattern(124.93178509991021, 81, {'task-3': 0, 'task-4': 1, 'task-6': 0}),
            instance.Pattern(38.07012128285633, 23, {'task-3': 1, 'task-9': 0}),
            instance.Pattern(52.69048404895649, 47, {'task-0': 1}),
            instance.Pattern(35.62329788205275, 27, {'task-6': 1}),
            instance.Pattern(93.95823413565259, 55, {'task-2': 0, 'task-7': 1}),
            instance.Pattern(17.505025126061817, 25, {'task-1': 1, 'task-9': 0}),
            instance.Pattern(154.62559227316274, 80, {'task-3': 0, 'task-4': 0}),
            instance.Pattern(12.992342504169876, 11, {'task-5': 1, 'task-9': 0}),
            instance.Pattern(153.72789714623414, 82, {'task-1': 0, 'task-9': 1, 'task-14': 0}),
            instance.Pattern(163.11021645077446, 68, {'task-3': 1, 'task-4': 0, 'task-6': 0}),
            instance.Pattern(174.28247373231412, 68, {'task-4': 0, 'task-8': 0, 'task-11': 1, 'task-12': 0}),
            instance.Pattern(275.52252821851215, 96, {'task-2': 1, 'task-6': 0, 'task-7': 0, 'task-14': 0}),
            instance.Pattern(8.553100415693567, 11, {'task-9': 0}),
            instance.Pattern(225.40616277721884, 81, {'task-0': 0, 'task-2': 0, 'task-6': 0, 'task-7': 1}),
            instance.Pattern(219.67854090006733, 87, {'task-1': 0, 'task-13': 0, 'task-14': 1}),
            instance.Pattern(79.14704397924928, 81, {'task-4': 1}),
            instance.Pattern(84.11209173195388, 65, {'task-6': 0, 'task-14': 1}),
            instance.Pattern(264.6167001840266, 96, {'task-0': 0, 'task-2': 1, 'task-7': 0}),
            instance.Pattern(156.63330741914393, 87, {'task-3': 0, 'task-4': 1, 'task-10': 0}),
            instance.Pattern(209.1505515020119, 87, {'task-3': 1, 'task-4': 0, 'task-10': 0}),
            instance.Pattern(129.97556030620345, 73, {'task-0': 1, 'task-1': 0, 'task-9': 0})]

for ii in range(2):
    mm = MasterModel(patterns, env.major_frame_length, tasks)
    mm.model.setParam("OutputFlag", 0)
    mm.model.setParam("OptimalityTol", 1e-9)
    #mm.model.setParam("Presolve", 0)  # When presolve is turned on -> one pattern is generated multiple times
    mm.solve()

    if not mm.feasible:
        print("master not feasible")
        
    for x in range(len(mm.alpha)):
        print(mm.alpha[x].X)

    pi0, pit = mm.get_dual_prices()
    print("dual prices", pi0)
    for x in pit:
        print(x, pit[x])    

    ss = SubproblemModelILP(env, acs, (pi0, pit), on_same, on_diff)
    ss.model.setParam("OutputFlag", 0)
    ss.model.setParam("OptimalityTol", 1e-9)
    ss.solve()
    
    print("subproblem obj", ss.model.ObjVal)


    if not ss.feasible:
        print("subproblem not feasible")
                
    EPS = 1e-4
    if ss.model.ObjVal >= -EPS:  # no more improving patterns exist
        print("subproblem non negative")
    else:
        p = ss.get_pattern()
        print("  found pattern {:s}, {:s}".format(str(p.to_dict()), str(ss.model.ObjVal)))
        patterns.append(p)      

"""
INFO:root:  found pattern {'cost': 48.756073188994, 'length': 31, 'task_mapping': {'task-10': 1}}, -0.0010344189839255336
INFO:root:  found pattern {'cost': 48.756073188994, 'length': 31, 'task_mapping': {'task-10': 1}}, -0.0010344189839255336
"""
