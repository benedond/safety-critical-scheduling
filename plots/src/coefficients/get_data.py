#!/usr/bin/python3
import pandas as pd

def get_ips(chars_file):
    df = pd.read_csv(chars_file)
    df = df[["benchmark", "affinity", "slope", "intercept"]]     
    df["affinity"] = df["affinity"].apply(lambda x: "little" if x in ["A53", "A57"] else "big")
    return df     
    
    
if __name__ == "__main__":     
    df_imx8a = get_ips("../../../data/characteristics-imx8a-all.csv")
    df_imx8b = get_ips("../../../data/characteristics-imx8b-all.csv")
    df_tx2 = get_ips("../../../data/characteristics-tx2-all.csv")
      
    # Merge to a single df
    df = df_imx8a.merge(df_imx8b, on=['benchmark','affinity'], how='inner', suffixes=('imxa', ''))
    df = df.merge(df_tx2, on=['benchmark','affinity'], how='inner', suffixes=('imxb', 'tx'))
    
    # save little and big separately
    df_little = df[df["affinity"] == "little"]
    df_big = df[df["affinity"] == "big"]
    
    df_little.to_csv("./parameters_little.csv", index=False)
    df_big.to_csv("./parameters_big.csv", index=False)