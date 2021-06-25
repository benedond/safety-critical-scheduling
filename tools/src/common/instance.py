from enum import IntEnum
from typing import Mapping, List, Dict
import json
import sys

# class Instance:
#     def __init__(self, data) -> None:
#         """
#         INPUT:
#         data - json contaiing the instance parameters
#         """
#         self.data = data

#     def __str__(self) -> str:
#         return json.dumps(self.data, indent=2)

#     def get_h(self) -> int:
#         return self.data["environment"]["majorFrameLength"]

#     def get_processors(self) -> List[dict]:
#         return self.data["environment"]["processors"]

#     def get_task_ids(self):
#         return sorted([t["task"] for t in self.data["assignmentCharacteristics"]])


"""
class Job:

    __slots__ = [
        'id',
        'index',
        'machine_idx',
        'processing_time'
    ]

    def __init__(self, job_id: int, index: int, machine_idx: int, processing_time: int):
        self.id = job_id
        self.index = index
        self.machine_idx = machine_idx
        self.processing_time = processing_time

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id 
"""


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

    @staticmethod
    def from_json(s: str, instance_filename: str = None):
        inst_raw = json.loads(s)

        pass

        return Environment()

class ProcessorAssignment:
    __slots__ = [
        'processor',
        'processing_units'
    ]

    def __init__(self, processor: str, processing_units: int):
        self.processor = processor
        self.processing_units = processing_units


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


class Window:
    __slots__ = [
        'length',
        'task_assignments'
    ]

    def __init__(self, length: int, task_assignments: List[TaskAssignment]):
        self.length = length
        self.task_assignments = task_assignments


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


def parse_environment(s: dict) -> Environment:
    env = None
    if "environment" not in s:
        print("warning: parse_environment called, but no environment data was found in source json", file=sys.stderr)
    else:        
        # Parse the processors
        processors = []    
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
            processors.append(Processor(p_name, p["processingUnits"], processor_type))
            processors_list.append(p_name)

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
    else:
        print("warning: parse_solution called, but no solution was found in source json", file=sys.stderr)

    return solution


def read_json_from_file(path: str) -> dict:
    data = {}
    with open(path, "r") as f_in:
        data = json.load(f_in)
    return data


def write_to_file(data: dict, path:str):
    with open(path, "w") as f_out:
        json.dump(data, f_out)


def get_val(dct, key, default):
    """Get value from dct[key]; if not defined, return default value"""
    if key in dct and dct[key]:
        return dct[key]
    return default


# void write_assignment_characteristics(nlohmann::json& json, const std::vector<assignment_characteristic>& tasks);
# void write_tasks(nlohmann::json& json, const std::vector<task>& tasks);
# void write_solution(nlohmann::json& json, const solution& solution);


if __name__ == "__main__":
    data = read_json_from_file("./data/all_fields.json")
    env = parse_environment(data)
    tasks = parse_tasks(data)
    sol = parse_solution(data)
    ass_char = parse_assignment_characteristics(data)