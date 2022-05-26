#!/usr/bin/python3
import pandas as pd

def get_ips(chars_file, cluster, factor):
    df = pd.read_csv(chars_file)
    df = df[df["affinity"] == cluster][["benchmark", "runtime"]]
    df["runtime"] = df["runtime"] * factor
    
    return df     
    
    
if __name__ == "__main__": 
    df_imx8a = get_ips("../../../data/characteristics-imx8a-all.csv", "A53", 1596/1200)
    df_imx8b = get_ips("../../../data/characteristics-imx8b-all.csv", "A53", 1596/1200)
    df_tx2 = get_ips("../../../data/characteristics-tx2-all.csv", "A57", 1.0)
    
    # Merge to a single df
    df = df_imx8a.merge(df_imx8b, on='benchmark', how='inner', suffixes=('_imx8a', ''))
    df = df.merge(df_tx2, on='benchmark', how='inner', suffixes=('_imx8b', '_tx2'))

    # save
    df.to_csv("./speedup.csv", index=False)    