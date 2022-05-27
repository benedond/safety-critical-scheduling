#!/usr/bin/python3
import pandas as pd

def get_ips(chars_file, nonneg=False):
    df = pd.read_csv(chars_file)
    df = df[["benchmark", "affinity", "slope", "intercept"]]     
    df["affinity"] = df["affinity"].apply(lambda x: "little" if x in ["A53", "A57"] else "big")

    if nonneg:
        df["slope"] = df["slope"].apply(lambda x: x if x >= 0 else 0.001)
        df["intercept"] = df["intercept"].apply(lambda x: x if x >= 0 else 0.001)

    return df     

def get_df(nonneg=False):
    df_imx8a = get_ips("../../../data/characteristics-imx8a-all.csv", nonneg)
    df_imx8b = get_ips("../../../data/characteristics-imx8b-all.csv", nonneg)
    df_tx2 = get_ips("../../../data/characteristics-tx2-all.csv", nonneg)
      
    # Merge to a single df
    df = df_imx8a.merge(df_imx8b, on=['benchmark','affinity'], how='inner', suffixes=('imxa', ''))
    df = df.merge(df_tx2, on=['benchmark','affinity'], how='inner', suffixes=('imxb', 'tx'))

    return df  
    
if __name__ == "__main__":     
    df = get_df(False)
    # save little and big separately
    df_little = df[df["affinity"] == "little"]
    df_big = df[df["affinity"] == "big"]
    df_little.to_csv("./parameters_little.csv", index=False)
    df_big.to_csv("./parameters_big.csv", index=False)

    # Save with non-neg coeffs
    df = get_df(True)
    # save little and big separately
    df_little = df[df["affinity"] == "little"]
    df_big = df[df["affinity"] == "big"]
    df_little.to_csv("./parameters_little_nneg.csv", index=False)
    df_big.to_csv("./parameters_big_nneg.csv", index=False)