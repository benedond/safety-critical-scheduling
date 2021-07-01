#! /usr/bin/python3
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common import arg_parser
from common import instance
import csv

if __name__ == "__main__":
    ap = arg_parser.ArgParser()    
    fieldnames = ['instance', 'solver', 'time', 'objective-reported', 'objective', 'length']    
    
    # Prepare output file
    f_out = sys.stdout    
    output_filename = ap.get_arg_value("--output")
    if output_filename:
        f_out = open(output_filename, "a")

    writer_obj = csv.DictWriter(f_out, fieldnames=fieldnames)
    
    # Iterate through the given path
    path = ap.get_arg_value("--folder")
    if not path:        
        print("--folder parameter needs to be specified.", file=sys.stderr)
        exit(1)

    writer_obj.writeheader()
    # - write info        
    for f in sorted(os.listdir(path)):
        print(f)
        if f.endswith(".out"):
            data = instance.read_json_from_file(os.path.join(path,f))
            sol = instance.parse_solution(data)
            inst = f
            solver = sol.solver_name
            time = sol.solution_time
            objective_rep = -1
            objective = instance.get_solution_objective(data)
            length = instance.get_solution_length(sol)
            
            if sol.solver_metadata and "objective" in sol.solver_metadata:
                objective_rep = sol.solver_metadata["objective"]
                
            writer_obj.writerow({"instance": inst,
                                 "solver": solver,
                                 "time": time,
                                 "objective-reported": objective_rep,
                                 "objective": objective,
                                 "length": length})
            
    f_out.close()
            
            
            
    
    
    
