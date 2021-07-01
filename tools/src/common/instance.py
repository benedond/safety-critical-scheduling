from enum import IntEnum
from typing import Mapping, List, Dict
import json
import sys


class ProcessorType(IntEnum):
    InvalidType = 0,
    MainProcessor = 1,
    Coprocessor = 2


class Processor:
    __slots__ = [
        'name',
        'processing_units',
        'processor_type'
    ]

    def __init__(self, name: str, processing_units: int, processor_type: ProcessorType):
        self.name = name
        self.processing_units = processing_units
        self.processor_type = processor_type

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "processingUnits": self.processing_units,
            "type": self.processor_type
        }            

class Environment:
    __slots__ = [
        'processors',
        'processors_list',
        'major_frame_length',
        'problem_version',
        'sc_part'
    ]

    def __init__(self, processors: Mapping[str, Processor], processors_list: List[Processor], major_frame_length: int, problem_version: int, sc_part: float):
        self.processors = processors
        self.processors_list = processors_list
        self.major_frame_length = major_frame_length
        self.problem_version = problem_version
        self.sc_part = sc_part

    def to_dict(self) -> dict:
        return {
            "majorFrameLength": self.major_frame_length,
            "problemVersion": self.problem_version,
            "scPart": self.sc_part,
            "processors": [p.to_dict() for p in self.processors]
        }

class ProcessorAssignment:
    __slots__ = [
        'processor',
        'processing_units'
    ]

    def __init__(self, processor: str, processing_units: int):
        self.processor = processor
        self.processing_units = processing_units

    def to_dict(self) -> dict:
        return {
            "processor": self.processor,
            "processingUnits": self.processing_units
        }


class Task:
    __slots__ = [
        'name',
        'command',
        'length',
        'assignment_index',
        'processors'
    ]

    def __init__(self, name: str, command: str, length: int, assignment_index: int, processors: List[ProcessorAssignment]):
        self.name = name
        self.command = command
        self.length = length
        self.assignment_index = assignment_index
        self.processors = processors

    def to_dict(self) -> dict:
        return {
            "assignmentIndex": self.assignment_index,
            "command": self.command,
            "length": self.length,
            "name": self.name,
            "processors": [ac.to_dict() for ac in self.processors]
        }


class ResourceAssignment:
    __slots__ = [
        'slope',
        'intercept',
        'length',
        'processors'
    ]

    def __init__(self, slope: float, intercept: float, length: int, processors: List[ProcessorAssignment]):
        self.slope = slope
        self.intercept = intercept
        self.length = length
        self.processors = processors

    def to_dict(self) -> dict:
        return {
            "slope": self.slope,
            "intercept": self.intercept,
            "length": self.length,
            "processors": [pa.to_dict() for pa in self.processors]
        }


class AssignmentCharacteristic:
    __slots__ = [
        'task',
        'command',
        'resource_assignmnets'
    ]

    def __init__(self, task: str, command: str, resource_assignmnets: List[ResourceAssignment]):
        self.task = task
        self.command = command
        self.resource_assignmnets = resource_assignmnets

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "command": self.command,
            "resourceAssignments": [ra.to_dict() for ra in self.resource_assignmnets]
        }


class TaskAssignment:
    __slots__ = [
        'task',
        'processor',
        'processing_unit',
        'start',
        'length'
    ]

    def __init__(self, task: str, processor: str, processing_unit: int, start: int, length: int):
        self.task = task
        self.processor = processor
        self.processing_unit = processing_unit
        self.start = start
        self.length = length

    def to_dict(self) -> dict:
        return {
            "length": self.length,
            "processingUnit": self.processing_unit,
            "processor": self.processor,
            "start": self.start,
            "task": self.task
        }


class Window:
    __slots__ = [
        'length',
        'task_assignments'
    ]

    def __init__(self, length: int, task_assignments: List[TaskAssignment]):
        self.length = length
        self.task_assignments = task_assignments

    def to_dict(self) -> dict:
        return {
            "length": self.length,
            "tasks": [ta.to_dict() for ta in self.task_assignments]
        }


class Solution:
    __slots__ = [
        'feasible',
        'solver_name',
        'solution_time',
        'solver_metadata',
        'windows'
    ]

    def __init__(self, feasible: bool, solver_name: str, solution_time: int, solver_metadata: Dict[str, str], windows: List[Window]):
        self.feasible = feasible
        self.solver_name = solver_name
        self.solution_time = solution_time
        self.solver_metadata = solver_metadata
        self.windows = windows

    def to_dict(self) -> dict:
        return {
            "feasible": self.feasible,
            "solutionTime": self.solution_time,
            "solverMetadata": self.solver_metadata,
            "solverName": self.solver_name,
            "windows": [w.to_dict() for w in self.windows]
        }


def parse_environment(s: dict) -> Environment:
    env = None
    if "environment" not in s:
        print("warning: parse_environment called, but no environment data was found in source json", file=sys.stderr)
    else:        
        # Parse the processors
        processors = {}    
        processors_list = []
        for p in s["environment"]["processors"]:
            p_name = p["name"]
            # - decode the type
            processor_type = ProcessorType.InvalidType
            p_type = p["type"]
            if p_type == "main_processor":
                processor_type = ProcessorType.MainProcessor
            elif p_type == "coprocessor":
                processor_type = ProcessorType.Coprocessor
            
            # - create new processor
            proc = Processor(p_name, p["processingUnits"], processor_type)
            processors[proc.name] = proc
            processors_list.append(proc)

        # Parse major frame length
        major_frame_length = s["environment"]["majorFrameLength"]

        # Parse problem version
        problem_version = s["environment"]["problemVersion"]

        # Parse SC part
        sc_part = get_val(s["environment"], "scPart", 0.6)

        # Create new environment
        env = Environment(processors, processors_list, major_frame_length, problem_version, sc_part)
    return env
    

def parse_tasks(s: dict) -> Mapping[str, Task]:
    task_map = {}
    
    if "tasks" not in s:
        print("warning: parse_tasks called, but no tasks were found in source json", file=sys.stderr)
    else:
        for t in s["tasks"]:
            t_name = t["name"]
            t_cmd = get_val(t, "command", "")
            t_ass_idx = get_val(t, "assignmentIndex", -1)
            
            t_pas = []
            for t_ass in t["processors"]:
                t_pas.append(ProcessorAssignment(t_ass["processor"], t_ass["processingUnits"]))

            task_map[t_name] = Task(t_name, t_cmd, t["length"], t_ass_idx, t_pas)

    return task_map

# assignment_characteristic_list parse_assignment_characteristics(const nlohmann::json& json);
def parse_assignment_characteristics(s: dict) -> List[AssignmentCharacteristic]:
    ac_list = []
    if "assignmentCharacteristics" not in s:
        print("warning: parse_assignment_characteristics called, but no assignment characteristics were found in source json", file=sys.stderr)
    else:
        ac_list = []

        for a in s["assignmentCharacteristics"]:
            a_cmd = get_val(a, "command", "")
            a_char = AssignmentCharacteristic(a["task"], a_cmd, [])

            for r in a["resourceAssignments"]:
                res_assignment = ResourceAssignment(r["slope"], r["intercept"], r["length"], [])

                for p in r["processors"]:
                    res_assignment.processors.append(ProcessorAssignment(p["processor"], p["processingUnits"]))

                a_char.resource_assignmnets.append(res_assignment)

            ac_list.append(a_char)
    
    return ac_list

# solution parse_solution(const nlohmann::json& json);
def parse_solution(s: dict) -> Solution:
    solution = None

    if "solution" in s:
        s_feasible = get_val(s["solution"], "feasible", False)
        s_solver_name = get_val(s["solution"], "solverName", "unnamed solver")
        s_solution_time = get_val(s["solution"], "solutionTime", -1)
        s_solver_metadata = {}
        s_windows = []

        if "solverMetadata" in s["solution"] and s["solution"]["solverMetadata"]:
            for k in s["solution"]["solverMetadata"]:
                s_solver_metadata[k] = s["solution"]["solverMetadata"][k]

        if "windows" in s["solution"]:
            for w in s["solution"]["windows"]:
                task_assignments = []
                if "tasks" in w:
                    for t_ass in w["tasks"]:
                        task_assignments.append(TaskAssignment(t_ass["task"], t_ass["processor"], t_ass["processingUnit"], t_ass["start"], t_ass["length"]))
                else:
                    print("warning: window is empty", file=sys.stderr)
                
                s_windows.append(Window(w["length"], task_assignments))
        else:            
            print("info: solution has no windows", file=sys.stderr)

        solution = Solution(s_feasible, s_solver_name, s_solution_time, s_solver_metadata, s_windows)
    else:
        print("warning: parse_solution called, but no solution was found in source json", file=sys.stderr)

    return solution


def get_solution_length(sol: Solution):
    return sum([w.length for w in sol.windows]) if sol.windows else 0

def  get_solution_objective(data: dict):
    sol = parse_solution(data)
    tasks = parse_tasks(data)
    ascs = parse_assignment_characteristics(data)
    env = parse_environment(data)        
    
    # Prepare resource assignments for the individual tasks
    task_to_ra = {}    
    for t in tasks:                
        for asc in ascs:
            if t == asc.task:                
                task_to_ra[t] = asc.resource_assignmnets[tasks[t].assignment_index]
    obj = 0
    for w in sol.windows:
        print("window", w.length)        
        print("A", [task_to_ra[t.task].slope * task_to_ra[t.task].length for t in w.task_assignments])
        print("B", [task_to_ra[t.task].intercept * w.length for t in w.task_assignments])
        A_j = sum([task_to_ra[t.task].slope * task_to_ra[t.task].length for t in w.task_assignments])
        B_j = max([task_to_ra[t.task].intercept * w.length for t in w.task_assignments])
        print("sum A", A_j)
        print("max B", B_j)
        obj += A_j + B_j
    
    obj /= env.major_frame_length    
    return obj
def read_json_from_file(path: str) -> dict:
    data = {}
    with open(path, "r") as f_in:
        data = json.load(f_in)
    return data


def write_to_file(data: dict, path:str):
    with open(path, "w") as f_out:
        json.dump(data, f_out, indent=4)


def get_val(dct, key, default):
    """Get value from dct[key]; if not defined, return default value"""
    if key in dct and (dct[key] is not None):
        return dct[key]
    return default


def write_tasks(s: dict, tasks: List[Task]):
    s["tasks"] = [t.to_dict() for t in tasks]

    
def write_solution(s: dict, sol: Solution):
    s["solution"] = sol.to_dict()


# def write_assignment_characteristics(data: dict, ac: List[AssignmentCharacteristic]):

if __name__ == "__main__":
    data = read_json_from_file("./data/all_fields.json")
    env = parse_environment(data)
    tasks = parse_tasks(data)
    sol = parse_solution(data)
    ass_char = parse_assignment_characteristics(data)

    print(env.to_dict())
    print(sol.to_dict())