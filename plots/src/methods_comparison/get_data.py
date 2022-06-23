#!/usr/bin/python3
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--relative", "-r", dest='relative', default=False, action='store_true', help="Use relative power/temperature (w.r.t. idle)?")

# These temperatures might not be very precise, also it might heavily depend on the T_amb
T_idle = {"imx8a": 46, "imx8b": 40, "tx2": 38}

def get_df(res_file, relative: bool=False):
    df = pd.read_csv(res_file)    
    P_idle = (df["power"] - df["power_offset"]).mean()
    
    if relative:
        df["power"] -= P_idle
        # relative w.r.t T_idle
        #df["temp-little"] -= T_idle["imx8a" if "imx8a" in res_file else ("imx8b" if "imx8b" in res_file else "tx2")]
        #df["temp-big"] -= T_idle["imx8a" if "imx8a" in res_file else ("imx8b" if "imx8b" in res_file else "tx2")]
        # relative w.r.t. T_amb
        df["temp-little"] -= df["ambient"]
        df["temp-big"] -= df["ambient"]
    else:
        df["obj_sm"] += P_idle
        df["obj_lr"] += P_idle 
        df["obj_lr_ub"] += P_idle
    
    df["solver"] = df.apply(lambda row: row.solver if row.solver != "ILP-SM-I" else "ILP-SM", axis=1)
    
    
    df["inst_id"] = df.apply(lambda row: row.instance.split("-")[0], axis=1)
    df = df.round({'temp-little': 1, 'temp-big': 1, 'power': 2})
    df["solver"] = df["solver"].str.upper()
    
    
    return df[["inst_id", "solver", "obj_sm", "obj_lr", "obj_lr_ub", "power", "temp-little","temp-big"]]


if __name__ == "__main__":  
    args = parser.parse_args()    
  
    experiments = ["imx8a-all", "imx8a-cpu", "imx8b-all", "imx8b-cpu", "tx2-all", "tx2-cpu"]
    # Get some reasonable order of solvers
    df = get_df("../../../experiments/04_solvers_thermal_evaluation/results/{}.csv".format(experiments[1]))
    df = df.sort_values(by=["power"])
    solvers = df["solver"].unique()
    solvers = [s for s in solvers if s != "ILP-SM-II"]
    
    #solvers = ["ILP-SM-I", "HEUR", "BB-SM", "ILP-IDLE-MIN", "QP-LR-UB", "BB-LR", "ILP-IDLE-MAX"]
    
    dct_res = {m: {e: None for e in experiments} for m in solvers}
    dfs = dict()

    for heur in solvers:
        for e in experiments:     
            df = get_df("../../../experiments/04_solvers_thermal_evaluation/results/{}.csv".format(e), args.relative)
            df_h = df[df["solver"] == heur]        
            dct_res[heur][e] = {"big": {"min":df_h["temp-big"].min(), "max": df_h["temp-big"].max(), "avg": df_h["temp-big"].mean(), "std": df_h["temp-big"].std()},
                                "little": {"min":df_h["temp-little"].min(), "max": df_h["temp-little"].max(), "avg": df_h["temp-little"].mean(), "std": df_h["temp-little"].std()}
            }

    # Save CSV for temperature graphs
    for e in experiments:
        df = pd.DataFrame(columns=["method", "T-little", "T-big"])

        for m in solvers:
            df.loc[len(df)] = [m, dct_res[m][e]["little"]["avg"], dct_res[m][e]["big"]["avg"]]
        
        #df = df.sort_values(by=["T-big"])
        df.to_csv("./temp_{}_{}.csv".format(e, "relative" if args.relative else "absolute"), index=False)    
    
    # Save CSV for power tables
    #for e in experiments:
    #    df_data = get_df("../../../experiments/04_solvers_thermal_evaluation/results/{}.csv".format(e), args.relative)
    #    df = pd.DataFrame(columns=["method"] + [f"inst{i}" for i in range(len(df_data["inst_id"].unique()))])
        
    #    for m in solvers:
    #        df_m = df_data[df_data["solver"] == m]
    #        df.loc[len(df)] = [m] + list(df_m["power"])
            
    #    df.to_csv("./power_{}_{}.csv".format(e, "relative" if args.relative else "absolute"), index=False)
    
    # joined CSV
    for e in ["imx8a", "imx8b", "tx2"]:
        df_all = get_df("../../../experiments/04_solvers_thermal_evaluation/results/{}-all.csv".format(e), args.relative)
        df_cpu = get_df("../../../experiments/04_solvers_thermal_evaluation/results/{}-cpu.csv".format(e), args.relative)
        
        df = pd.DataFrame(columns=["method"] + [f"inst{i}-all" for i in range(len(df_all["inst_id"].unique()))] + [f"inst{i}-cpu" for i in range(len(df_cpu["inst_id"].unique()))])
        
        for m in solvers:
            df_all_m = df_all[df_all["solver"] == m]
            df_cpu_m = df_cpu[df_cpu["solver"] == m]
            df.loc[len(df)] = [m] + list(df_all_m["power"]) + list(df_cpu_m["power"])
            
        df.to_csv("./power_{}_{}.csv".format(e, "relative" if args.relative else "absolute"), index=False)
   
    
