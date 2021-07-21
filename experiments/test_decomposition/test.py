import pandas as pd
import sys
import os

path = sys.argv[1]
num = int(sys.argv[2])

df = pd.read_csv(path)
 

for i in range(num):
    obj1 = float(df[(df["instance"]=="IN_{:03d}.json-global.out".format(i))]["objective"])
    obj2 = float(df[(df["instance"]=="IN_{:03d}.json-bap.out".format(i))]["objective"])
    if (obj1 != obj2):
        print(i, obj1, obj2, obj2-obj1)

