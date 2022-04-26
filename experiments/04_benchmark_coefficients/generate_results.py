#!/usr/bin/env python3
import argparse
import os
import sys
import pandas as pd
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import utils

parser = argparse.ArgumentParser()
parser.add_argument("--env_file",   "-e", type=str, required=True, help="Path to the environment file.")
parser.add_argument("--bench_file",   "-b", type=str, required=True, help="Path to the benchmark file.")
parser.add_argument("--meas_folder",  "-m", type=str, required=True, help="Path to the folder containing measurements.")
parser.add_argument("--out_folder", "-o", type=str, required=True, help="Path to the folder where to store the results.")

"""
Go through all the files with measurements in the given "path" and produce a dict mapping
(bench, cluster) -> {one: ..., all: ...}
"""
def read_data(path: str):
    def add_to_dct(dct, bench, cluster, cores, value):
        if (bench,cluster) not in dct:
            dct[(bench,cluster)] = dict()
        dct[(bench,cluster)][cores] = value
        
    dct = dict()
    
    for f in os.listdir(path):
        bench, cluster, cores = f.split(".")[0].split("_")
        # Compute the power consumption
        value = utils.get_power_from_measurement_file(os.path.join(path, f))
        add_to_dct(dct, bench, cluster, cores, value)
        
    return dct
        

def get_intercept_and_slope(power_one, power_all, n_cores):
    slope = (power_all - power_one) / (n_cores - 1)
    intercept = power_one - slope
    return intercept, slope


def get_bench_cmds(bench, bench_file):
    df = pd.read_csv(bench_file)
    cmds = dict()
    for b in bench:
        if b == "sleep":
            cmds[b] = "sleep inf"
        else:
            cmds[b] = df[df["benchmark"] == b].iloc[0]["command"]
    return cmds

def generate_characteristics(env_file_path: str, bench_file_path:str, measurements_path: str, out_path: str):
    d = read_data(measurements_path)
    idle_power = utils.get_idle_power(env_file_path)
    cmds = get_bench_cmds([x[0] for x in d.keys()], bench_file_path)
    df = pd.DataFrame(columns=("benchmark", "affinity", "intercept", "slope", "runtime", "command"))    
    for bench, aff in d.keys():
        n_cores = utils.get_n_cores(args.env_file, aff)
        intercept, slope = get_intercept_and_slope(d[(bench, aff)]["one"], d[(bench,aff)]["all"], n_cores)
        
        first_core = utils.get_first_core(env_file_path, aff)        
        ips = utils.get_value_per_second(os.path.join(measurements_path, "{}_{}_one.json.yaml.csv".format(bench, aff)),
                                         "CPU{}_work_done".format(first_core))
        
        cmd = cmds[bench]
        
        # benchmark,affinity,intercept,slope,runtime,command        
        df.loc[len(df)] = [bench, aff, intercept, slope, 1/ips if ips else None, cmd]              
    
    # compensate the idle state (subtract the mean measured idle power consumption)    
    df["intercept"] -= idle_power
    
    df = df.sort_values("benchmark")    
    df.to_csv(out_path, index=False)        


if __name__ == "__main__":
    args = parser.parse_args()
    generate_characteristics(args.env_file, args.bench_file, args.meas_folder, args.out_folder)
    