#! /usr/bin/python3

import sys
import os
import json
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '../../tools/src/common'))
import instance

lr_coefficients = {
	"imx8a": {"A53": {"slope": 1.252, "intercept": 0.273},    "A72": {"slope": 0.484, "intercept": 0.529}},
    "imx8b": {"A53": {"slope": 1.133, "intercept": 0.234},    "A72": {"slope": 0.413, "intercept": 0.526}},
    "tx2":   {"A72": {"slope": 0.000, "intercept": 0.000}, "Denver": {"slope": 0.000, "intercept": 0.000}}
}

if __name__ == "__main__":
    inst_path = "./solutions/scalability/imx8a/IN_10_2.json-QP-LR-UB.out" 
    with open(inst_path, "r") as f_in:
         data = json.load(f_in)
         instance.analyze_solution(data, lr_coefficients["imx8a"])

