#!/usr/bin/python3
import pandas as pd

# how many iterations are done per benchmarks (reported as a single iteration (-i param for EEMBC kernels))
bench_factor = {"a2time-4K": 100,
                "a2time-4M": 100,
                "aifirf-4K": 100,
                "aifirf-4M": 10,
                "bitmnp-4K": 100,
                "bitmnp-4M": 100,
                "canrdr-4K": 100,
                "canrdr-4M": 100,
                "idctrn-4K": 100,
                "idctrn-4M": 100,
                "iirflt-4K": 100,
                "iirflt-4M": 100,
                "matrix-4K": 100,
                "matrix-4M": 100,
                "membench-1K-RO-R": 1,
                "membench-1K-RO-S": 1,
                "membench-1K-RW-R": 1,
                "membench-1K-RW-S": 1,
                "membench-1M-RO-R": 1,
                "membench-1M-RO-S": 1,
                "membench-1M-RW-R": 1,
                "membench-1M-RW-S": 1,
                "membench-4M-RO-R": 1,
                "membench-4M-RO-S": 1,
                "membench-4M-RW-R": 1,
                "membench-4M-RW-S": 1,
                "pntrch-4K": 100,
                "pntrch-4M": 1,
                "puwmod-4K": 100,
                "puwmod-4M": 100,
                "rspeed-4K": 100,
                "rspeed-4M": 100,
                "tblook-4K": 100,
                "tblook-4M": 100,
                "tinyrenderer-boggie": 1,
                "tinyrenderer-diablo": 1,
                "ttsprk-4K": 100,
                "ttsprk-4M": 100,
}

def get_runtime(chars_file, cluster, factor):
    df = pd.read_csv(chars_file)
    df = df[df["affinity"] == cluster][["benchmark", "runtime"]]
    df["runtime"] = df["runtime"] * factor    
    return df     
    
def get_ips(chars_file, cluster):
    df = pd.read_csv(chars_file)
    df = df[df["affinity"] == cluster][["benchmark", "exec_time"]]
    df["ips"] = 1.0 / df["exec_time"]
    df["ips"] = df.apply(lambda row: row["ips"] * bench_factor[row["benchmark"]], axis = 1)
    return df[["benchmark", "ips"]]
    
if __name__ == "__main__": 
    df_imx8a = get_runtime("../../../data/characteristics-imx8a-all.csv", "A53", 1596/1200)
    df_imx8b = get_runtime("../../../data/characteristics-imx8b-all.csv", "A53", 1596/1200)
    df_tx2 = get_runtime("../../../data/characteristics-tx2-all.csv", "A57", 1.0)
    
    # Merge to a single df
    df = df_imx8a.merge(df_imx8b, on='benchmark', how='inner', suffixes=('_imx8a', ''))
    df = df.merge(df_tx2, on='benchmark', how='inner', suffixes=('_imx8b', '_tx2'))

    # save
    df.to_csv("./speedup.csv", index=False)    
    
    # Calculate IPS for each benchmark
    df_imx8a_little = get_ips("../../../data/characteristics-imx8a-all.csv", "A53")
    df_imx8a_big = get_ips("../../../data/characteristics-imx8a-all.csv", "A72")
    df = df_imx8a_little.merge(df_imx8a_big, on='benchmark', how='inner', suffixes=('imxlow', ''))
        
    df_imx8b_little = get_ips("../../../data/characteristics-imx8b-all.csv", "A53")
    df = df.merge(df_imx8b_little, on='benchmark', how='inner', suffixes=('imxhigh', ''))
    df_imx8b_big = get_ips("../../../data/characteristics-imx8b-all.csv", "A72")
    df = df.merge(df_imx8b_big, on='benchmark', how='inner', suffixes=('imxblow', ''))
    
    df_tx2_little = get_ips("../../../data/characteristics-tx2-all.csv", "A57")
    df = df.merge(df_tx2_little, on='benchmark', how='inner', suffixes=('imxbhigh', ''))
    df_tx2_big = get_ips("../../../data/characteristics-tx2-all.csv", "Denver")
    df = df.merge(df_tx2_big, on='benchmark', how='inner', suffixes=('txlow', 'txhigh'))
    
    df.to_csv("./ips.csv", index=False)    