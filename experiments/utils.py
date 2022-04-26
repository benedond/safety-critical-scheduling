#! /usr/bin/python3

# Some utils function to read, write and process data

import pandas as pd
import json
import os

def create_folder(out_folder):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

def read_json(file):
    f = open(file,"r")        
    data = json.loads(f.read())
    f.close()
    return data


def read_csv(file):
    return pd.read_csv(file, comment="#")    


def get_power_from_measurement_file(file):
    df = read_csv(file)
    df = df[["time/ms", "energy"]]
    df = df.dropna()
    
    if (len(df.index)) > 2:
        second = df.iloc[1]
        last = df.iloc[-1]
        
        return (last["energy"] - second["energy"]) / (last["time/ms"] - second["time/ms"]) * 1e3
        
    else:
        return 0.0
        
def get_value_per_second(file, col_name):
    df = read_csv(file)
    df = df[["time/ms", col_name]]
    df = df.dropna()
    
    if (len(df.index)) >= 2:
        first = df.iloc[0]
        last = df.iloc[-1]
        
        return (last[col_name] - first[col_name]) / (last["time/ms"] - first["time/ms"]) * 1e3
        
    else:
        return None
        
        
def get_n_cores(env_file_path: str, cluster: str):
    d = read_json(env_file_path)
    for p in d["environment"]["processors"]:
        if p["name"] == cluster:
            return p["processingUnits"]
    raise RuntimeException("Cluster {} not contained in environment file {}".format(cluster, env_file_path))
    
    
def get_first_core(env_file_path: str, cluster: str):
    d = read_json(env_file_path)
    for p in d["environment"]["processors"]:
        if p["name"] == cluster:
            return p["coreIds"][0]
    raise RuntimeException("Cluster {} not contained in environment file {}".format(cluster, env_file_path))
    
def get_idle_power(env_file_path: str):
    d = read_json(env_file_path)
    return d["environment"]["idlePower"]

