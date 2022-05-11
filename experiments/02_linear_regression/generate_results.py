#!/usr/bin/env python3
import argparse
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import sys
import json
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import utils

parser = argparse.ArgumentParser()
parser.add_argument("--char_file", "-c", type=str, required=True, help="Path to the benchmark characteristics file.")
parser.add_argument("--env_file", "-e", type=str, required=True, help="Path to the environment file.")
parser.add_argument("--results_file", "-r", type=str, required=True, help="Path to the results file containing power data.")
parser.add_argument("--mapping_file", "-m", type=str, required=True, help="Path to the mapping file (id -> bench).")
parser.add_argument("--out_file", "-o", type=str, required=True, help="Path to the output folder.")
parser.add_argument("--platform", "-p", type=str, required=True, help="Name of the platform (key in result file).")

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
    
    
    inst_chars = []
    powers = []
    idle_power = env["environment"]["idlePower"]
    
    for inst in df["instance"].unique():        
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
        cur_power = df[(df["instance"] == inst)]["power"].iloc[0]
        powers.append(cur_power - idle_power)  # center data (offset by idle power)
        
    # Make the linear regression
    reg = LinearRegression(fit_intercept=False, positive=True).fit(inst_chars, powers)
    
    print("Score:", reg.score(inst_chars, powers))
    print("Coeffs:", reg.coef_)
    print(reg.intercept_)
    print()
    
    
    res = env_and_coeffs_to_res(env, reg.coef_, reg.score(inst_chars, powers))    
    if os.path.isfile(args.out_file):
        # just append the result
        res_file = utils.read_json(args.out_file)
        res_file[args.platform] = res
        
    else:
        res_file = {args.platform: res}
    
    with open(args.out_file, "w") as f_out:
            json.dump(res_file, f_out, indent=4)
