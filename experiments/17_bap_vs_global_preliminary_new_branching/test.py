#!/usr/bin/env python3

import pandas as pd
import sys
import os

path = sys.argv[1]
num = int(sys.argv[2])

df = pd.read_csv(path)
 
print("instance, global, bap-pair, bap-task, diff")
for i in range(num):
    obj1 = float(df[(df["instance"]=="IN_{:03d}.json-global.out".format(i))]["objective"])
    obj2 = float(df[(df["instance"]=="IN_{:03d}.json-bap_pair.out".format(i))]["objective"])
    obj3 = float(df[(df["instance"]=="IN_{:03d}.json-bap_task.out".format(i))]["objective"])
    if (obj1 != obj2):
        print(i, obj1, obj2, obj3, obj2-obj1)
    if (obj1 != obj3):
        print(i, obj1, obj2, obj3, obj3-obj1)

