#!/usr/bin/env python3
import argparse
import numpy as np
from sklearn.linear_model import LinearRegression, HuberRegressor
import os
import sys
import json
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import utils
import pandas as pd
import random

parser = argparse.ArgumentParser()
parser.add_argument("--char_file", "-c", type=str, required=True, help="Path to the benchmark characteristics file.")
parser.add_argument("--env_file", "-e", type=str, required=True, help="Path to the environment file.")
parser.add_argument("--results_file", "-r", type=str, required=True, help="Path to the results file containing power data.")
parser.add_argument("--mapping_file", "-m", type=str, required=True, help="Path to the mapping file (id -> bench).")
parser.add_argument("--out_file", "-o", type=str, required=True, help="Path to the output folder.")
parser.add_argument("--platform", "-p", type=str, required=True, help="Name of the platform (key in result file).")
parser.add_argument("--tst_file", "-t", type=str, default="", help="Path to the test file (results of experiment 1), with instances and power_offset measurements.")

def env_and_coeffs_to_res(env, coeffs, score):
    return {
            env["environment"]["processors"][0]["name"]: {"slope": coeffs[0], "intercept": coeffs[1]},
            env["environment"]["processors"][1]["name"]: {"slope": coeffs[2], "intercept": coeffs[3]},
            "score": score
        }


if __name__ == "__main__":      
    args = parser.parse_args()
    
    env = utils.read_json(args.env_file)
    task_char = utils.read_csv(args.char_file)
    mapping = utils.read_json(args.mapping_file)
    df = utils.read_csv(args.results_file)
    tst = True if args.tst_file != "" else False
    
    inst_chars = []
    powers = []
    idle_power = env["environment"]["idlePower"]
    
        
    for index, row in df.iterrows():
        inst = row["instance"]
        benchmarks = list(map(lambda x: mapping[x], inst.split("_")))
        # little-slope, little-intercept, big-slope, big-intercept
        cur_chars = [0, 0, 0, 0]
        
        for little_idx in [0,1,2,3]:            
            _, slope, intercept = utils.get_cmd_slope_intercept(benchmarks[little_idx], env["environment"]["processors"][0]["name"], task_char)
            cur_chars[0] += slope
            cur_chars[1] += intercept
        for big_idx in [4,5]:
            _, slope, intercept = utils.get_cmd_slope_intercept(benchmarks[big_idx], env["environment"]["processors"][1]["name"], task_char)
            cur_chars[2] += slope
            cur_chars[3] += intercept
        
        inst_chars.append(cur_chars)    
        if row["instance"] == "0_0_0_0_0_0":
            powers.append(0.0)
        else:
            powers.append(row["power"] - idle_power)  # center data (offset by idle power)
    
    # Make the linear regression
    reg = LinearRegression(fit_intercept=False, positive=True).fit(inst_chars, powers)    
    #reg = HuberRegressor(fit_intercept=False).fit(inst_chars, powers)  # this regressor might be more robust to outliers
    
    print("Score:", reg.score(inst_chars, powers))
    print("Coeffs:", reg.coef_)
    print(reg.intercept_)
    print()
    
    if tst: # TEST: read one/all from file    
        df_tst = utils.read_csv(args.tst_file)        
        tst_chars = []
        tst_powers = []        
        for index, row in df_tst.iterrows():
            cur_chars = [0, 0, 0, 0]
            bench, proc, exp = row["instance"].split("_")
            _, slope, intercept = utils.get_cmd_slope_intercept(bench, proc, task_char)
            if proc == env["environment"]["processors"][0]["name"]:
                cur_chars[0] += slope * (1 if exp == "one" else utils.get_n_cores(args.env_file, proc))
                cur_chars[1] += intercept * (1 if exp == "one" else utils.get_n_cores(args.env_file, proc))
            elif proc == env["environment"]["processors"][1]["name"]:
                cur_chars[2] += slope * (1 if exp == "one" else utils.get_n_cores(args.env_file, proc))
                cur_chars[3] += intercept * (1 if exp == "one" else utils.get_n_cores(args.env_file, proc))
            else:
                raise Exception("{} name not known.".format(proc))
            
            tst_chars.append(cur_chars)
            tst_powers.append(row["power_offset"])
        
        print("TST Score:", reg.score(tst_chars, tst_powers))   
        
        # create csv file exporting the features
        data = [[i] + x + [y] for (i,x,y) in zip(list(df["instance"]), inst_chars, powers)]
        df_exp = pd.DataFrame(data, columns=["inst", "littleSlope", "littleIntercept", "bigSlope", "bigIntercept", "powerOffset"])   
        df_exp.to_csv("training_data.csv", index=False)
        
        data = [[i] + x + [y] for (i,x,y) in zip(list(df_tst["instance"]),tst_chars, tst_powers)]
        df_exp = pd.DataFrame(data, columns=["inst", "littleSlope", "littleIntercept", "bigSlope", "bigIntercept", "powerOffset"])   
        df_exp.to_csv("testing_data.csv", index=False)
        
    
    res = env_and_coeffs_to_res(env, reg.coef_, reg.score(inst_chars, powers))    
    if os.path.isfile(args.out_file):
        # just append the result
        res_file = utils.read_json(args.out_file)
        res_file[args.platform] = res
        
    else:
        res_file = {args.platform: res}
    
    with open(args.out_file, "w") as f_out:
            json.dump(res_file, f_out, indent=4)
