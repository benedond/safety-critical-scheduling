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
    
