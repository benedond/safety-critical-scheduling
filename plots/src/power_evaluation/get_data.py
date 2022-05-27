#!/usr/bin/python3
import pandas as pd

def get_df(res_file):
    df = pd.read_csv(res_file)
    P_idle = (df["power"] - df["power_offset"]).mean()
    
    df["obj_sm"] += P_idle
    df["obj_lr"] += P_idle 
    df["obj_lr_ub"] += P_idle

    return df[["instance", "obj_sm", "obj_lr", "obj_lr_ub", "power"]]
    
    
if __name__ == "__main__": 
    df_imx8a = get_df("../../../experiments/03_power_models_evaluation/results/scale-1x-imx8a-all.csv")
    df_imx8b = get_df("../../../experiments/03_power_models_evaluation/results/scale-1x-imx8b-all.csv")
    df_tx2 = get_df("../../../experiments/03_power_models_evaluation/results/scale-1x-tx2-all.csv")
    # Merge to a single df
    df = df_imx8a.merge(df_imx8b, on='instance', how='inner', suffixes=('_imx8a', ''))
    df = df.merge(df_tx2, on='instance', how='inner', suffixes=('_imx8b', '_tx2'))
    # save
    df = df.sort_values(by=["power_imx8a"])
    df.to_csv("./power_all.csv", index=False)    

    df_all = df

    df_imx8a = get_df("../../../experiments/03_power_models_evaluation/results/scale-1x-imx8a-cpu.csv")
    df_imx8b = get_df("../../../experiments/03_power_models_evaluation/results/scale-1x-imx8b-cpu.csv")
    df_tx2 = get_df("../../../experiments/03_power_models_evaluation/results/scale-1x-tx2-cpu.csv")
    # Merge to a single df
    df = df_imx8a.merge(df_imx8b, on='instance', how='inner', suffixes=('_imx8a', ''))
    df = df.merge(df_tx2, on='instance', how='inner', suffixes=('_imx8b', '_tx2'))
    # save
    df = df.sort_values(by=["power_imx8a"])
    df.to_csv("./power_cpu.csv", index=False)  

    df_cpu = df

    # Data for table
    def get_MAE(df, col, ref):
        col = abs(df[col] - df[ref])
        return round(col.mean(),2)

    with open("mae.tex", "w") as f:
        f.write("I.MX8~MEK & {} & {} & {} & {} & {} & {} \\\\ \n".format(
            get_MAE(df_all, "obj_sm_imx8a", "power_imx8a"),
            get_MAE(df_cpu, "obj_sm_imx8a", "power_imx8a"),
            get_MAE(df_all, "obj_lr_imx8a", "power_imx8a"),
            get_MAE(df_cpu, "obj_lr_imx8a", "power_imx8a"),
            get_MAE(df_all, "obj_lr_ub_imx8a", "power_imx8a"),
            get_MAE(df_cpu, "obj_lr_ub_imx8a", "power_imx8a"),
        ))
        f.write("I.MX8~Ixora & {} & {} & {} & {} & {} & {} \\\\ \n".format(
            get_MAE(df_all, "obj_sm_imx8b", "power_imx8b"),
            get_MAE(df_cpu, "obj_sm_imx8b", "power_imx8b"),
            get_MAE(df_all, "obj_lr_imx8b", "power_imx8b"),
            get_MAE(df_cpu, "obj_lr_imx8b", "power_imx8b"),
            get_MAE(df_all, "obj_lr_ub_imx8b", "power_imx8b"),
            get_MAE(df_cpu, "obj_lr_ub_imx8b", "power_imx8b"),
        ))
        f.write("TX2 & {} & {} & {} & {} & {} & {} \\\\ \n".format(
            get_MAE(df_all, "obj_sm_tx2", "power_tx2"),
            get_MAE(df_cpu, "obj_sm_tx2", "power_tx2"),
            get_MAE(df_all, "obj_lr_tx2", "power_tx2"),
            get_MAE(df_cpu, "obj_lr_tx2", "power_tx2"),
            get_MAE(df_all, "obj_lr_ub_tx2", "power_tx2"),
            get_MAE(df_cpu, "obj_lr_ub_tx2", "power_tx2"),
        ))