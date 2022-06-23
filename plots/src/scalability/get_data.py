#!/usr/bin/python3
import pandas as pd


def get_df(res_file, relative: bool=False):
    df = pd.read_csv(res_file)    
    
    df["time"] /= 1000.0 # scale to sec.
    df["time"] = df.apply(lambda row: min(300.0,row.time), axis=1)
    
    df["solver"] = df.apply(lambda row: row.solver if row.solver != "ILP-SM-I" else "ILP-SM", axis=1)

    df["inst_id"] = df.apply(lambda row: row.instance.split("_")[2], axis=1)
    #df = df.round({'time': 1})          
    
    df['n'] = df['n'].astype('int')
    
    return df[["inst_id", "n", "solver", "time"]]

def get_time(df, n, method, what):
    df_cur = df[(df["solver"] == method) & (df["n"] == n)]
    if what == "avg":        
        return df_cur["time"].mean()
    elif what == "std":
        return df_cur["time"].std()
    elif what == "min":
        return df_cur["time"].min()
    elif what == "max":
        return df_cur["time"].max()
    else:
        raise Exception("{} is not supported".format(what))

if __name__ == "__main__":      
    # Get some reasonable order of solvers
    df = get_df("../../../experiments/05_solvers_scalability/results/scalability-imx8a.csv")
    
    df = df.sort_values(by=["n", "inst_id"])
       
    methods = sorted(df["solver"].unique())    
    methods = [m for m in methods if m != "ILP-SM-II"]
    cols = ["n"] + [m + "_t-avg" for m in methods] + [m + "_t-std" for m in methods] + [m + "_t-min" for m in methods] + [m + "_t-max" for m in methods]
    
    df_res = pd.DataFrame(columns=cols)    
    for n in sorted(df["n"].unique()):
        df_res.loc[len(df_res)] = [int(n)] + [get_time(df, n, m, "avg") for m in methods] + [get_time(df, n, m, "std") for m in methods] + [get_time(df, n, m, "min") for m in methods] + [get_time(df, n, m, "max") for m in methods]
        
    df_res['n'] = df_res['n'].astype('int')
           
    df_res.to_csv("./times.csv", index=False)    