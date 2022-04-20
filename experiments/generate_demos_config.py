#!/usr/bin/env python3
import argparse
import utils
import os

"""
Generate DEmOS configuration files based on the prepared instances.
Also, generate visualizations of the schedules.

The only input path is the path to the instances. It is assumed that the script is executed from
the experiment folder, and the --inst_path represents the some path (experiment config) in ./instances folder.
"""

parser = argparse.ArgumentParser()
parser.add_argument("--inst_path", "-i", required=True, type=str, help="Path in './instances/... to the folder containing the instances.")


if __name__ == "__main__":
    args = parser.parse_args()    
    
    inst_path = os.path.join("./instances", args.inst_path)
    conf_path = os.path.join("./demos_configurations", args.inst_path)
    sched_path = os.path.join("./schedules", args.inst_path)
    
    print("Creating", conf_path)
    utils.create_folder(conf_path)
    print("Creating", sched_path)
    utils.create_folder(sched_path)
    
    if len(os.listdir(inst_path)) == len(os.listdir(conf_path)):
        print("Number of files in {} and {} is the same. Terminating...".format(inst_path, conf_path))
        exit(0)
    
    for f in os.listdir(inst_path):
        if os.path.isfile(os.path.join(conf_path, f + ".yaml")):
            print("Output file {} aleady exists.".format(f + ".yaml"))
        else:
            in_file = os.path.join(inst_path, f)
            out_file = os.path.join(conf_path, f + ".yaml")
            img_file = os.path.join(sched_path, f + ".png")
            
            # Export DEmOS config
            cmd = "./../../tools/bin/demos_config_export.exe --input {} --output {}".format(in_file, out_file)
            os.system(cmd)
            
            # add "set_cwd: false"
            data = ""
            with open(out_file, 'r') as original: data = original.read()
            with open(out_file, 'w') as modified: modified.write("set_cwd: false\n" + data)
            
            # Generate the schedule
            cmd = "./../../tools/bin/visualizer.exe --input {} --output {}".format(in_file, img_file)
            os.system(cmd)
        
