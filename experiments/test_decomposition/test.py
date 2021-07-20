import pandas as pd

df = pd.read_csv("stats.csv")

for i in range(100):
    obj1 = float(df[(df["instance"]=="IN_{:02d}.json-global.out".format(i))]["objective"])
    obj2 = float(df[(df["instance"]=="IN_{:02d}.json-bap.out".format(i))]["objective"])
    if (obj1 != obj2):
        print(i, obj1, obj2)

