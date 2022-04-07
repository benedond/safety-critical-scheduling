import pandas as pd

bench_to_cmd = {
    "a2time-4K" : "./a2time-4K -v0 -c1 -i100",
    "a2time-4M" : "./a2time-4M -v0 -c1 -i100",
    "aifirf-4K" : "./aifirf-4K -v0 -c1 -i100",
    "aifirf-4M" : "./aifirf-4M -v0 -c1 -i10",
    "bitmnp-4K" : "./bitmnp-4K -v0 -c1 -i100",
    "bitmnp-4M" : "./bitmnp-4M -v0 -c1 -i100",
    "canrdr-4K" : "./canrdr-4K -v0 -c1 -i100",
    "canrdr-4M" : "./canrdr-4M -v0 -c1 -i100",
    "idctrn-4K" : "./idctrn-4K -v0 -c1 -i100",
    "idctrn-4M" : "./idctrn-4M -v0 -c1 -i100",
    "iirflt-4K" : "./iirflt-4K -v0 -c1 -i100",
    "iirflt-4M" : "./iirflt-4M -v0 -c1 -i100",
    "matrix-4K" : "./matrix-4K -v0 -c1 -i100",
    "matrix-4M" : "./matrix-4M -v0 -c1 -i100",
    "pntrch-4K" : "./pntrch-4K -v0 -c1 -i100",
    "pntrch-4M" : "./pntrch-4M -v0 -c1 -i1",
    "puwmod-4K" : "./puwmod-4K -v0 -c1 -i100",
    "puwmod-4M" : "./puwmod-4M -v0 -c1 -i100",
    "rspeed-4K" : "./rspeed-4K -v0 -c1 -i100",
    "rspeed-4M" : "./rspeed-4M -v0 -c1 -i100",
    "tblook-4K" : "./tblook-4K -v0 -c1 -i100",
    "tblook-4M" : "./tblook-4M -v0 -c1 -i100",
    "ttsprk-4K" : "./ttsprk-4K -v0 -c1 -i100",
    "ttsprk-4M" : "./ttsprk-4M -v0 -c1 -i100",
    "membench-1K-RO-R" : "/root/thermobench/build/benchmarks/mem/membench -t1 -f -r -s 1000",
    "membench-1M-RO-R" : "/root/thermobench/build/benchmarks/mem/membench -t1 -f -r -s 1000000",
    "membench-4M-RO-R" : "/root/thermobench/build/benchmarks/mem/membench -t1 -f -r -s 4000000",
    "membench-1K-RW-R" : "/root/thermobench/build/benchmarks/mem/membench -t1 -f -r -w -s 1000",
    "membench-1M-RW-R" : "/root/thermobench/build/benchmarks/mem/membench -t1 -f -r -w -s 1000000",
    "membench-4M-RW-R" : "/root/thermobench/build/benchmarks/mem/membench -t1 -f -r -w -s 4000000",
    "membench-1K-RO-S" : "/root/thermobench/build/benchmarks/mem/membench -t1 -f -s 1000",
    "membench-1M-RO-S" : "/root/thermobench/build/benchmarks/mem/membench -t1 -f -s 1000000",
    "membench-4M-RO-S" : "/root/thermobench/build/benchmarks/mem/membench -t1 -f -s 4000000",
    "membench-1K-RW-S" : "/root/thermobench/build/benchmarks/mem/membench -t1 -f -w -s 1000",
    "membench-1M-RW-S" : "/root/thermobench/build/benchmarks/mem/membench -t1 -f -w -s 1000000",
    "membench-4M-RW-S" : "/root/thermobench/build/benchmarks/mem/membench -t1 -f -w -s 4000000",
    "tinyrenderer-boggie" : "/root/thermobench/build/benchmarks/tinyrenderer/tinyrenderer -f /root/thermobench/benchmarks/tinyrenderer/obj/boggie/*.obj",
    "tinyrenderer-diablo" : "/root/thermobench/build/benchmarks/tinyrenderer/tinyrenderer -f /root/thermobench/benchmarks/tinyrenderer/obj/diablo3_pose/*.obj",
}


df_little = pd.read_csv("parameters_little.csv")
df_little = df_little.rename(columns={"cluster": "affinity"})
df_big = pd.read_csv("parameters_big.csv")
df_big = df_big.rename(columns={"cluster": "affinity"})
df_big['runtime'] = 1

df_ips = pd.read_csv("ips_with_err.csv")
df_ips = df_ips.rename(columns={"cluster": "affinity"})


# IMX8A file
df_l = df_little.merge(df_ips, on='benchmark')
df_l = df_l[["benchmark", "affinity", "interceptimxa", "slopeimxa", "imxaRatio"]]
df_l = df_l.rename(columns={"interceptimxa": "intercept", "slopeimxa": "slope", "imxaRatio": "runtime"})

df_b = df_big[["benchmark", "affinity", "interceptimxa", "slopeimxa", "runtime"]]
df_b = df_b.rename(columns={"interceptimxa": "intercept", "slopeimxa": "slope"})

df_cur = pd.concat([df_l, df_b]).sort_index()
df_cur["affinity"] = df_cur.apply(lambda row: "A53" if row["affinity"] == "little" else "A72", axis=1)
df_cur["command"] = df_cur.apply(lambda row: bench_to_cmd[row["benchmark"]], axis=1)

df_cur = df_cur.sort_values(by=["benchmark", "affinity"])
df_cur.to_csv("characteristics-imx8a.csv", index=False)

# imx8b file
df_l = df_little.merge(df_ips, on='benchmark')
df_l = df_l[["benchmark", "affinity", "interceptimxb", "slopeimxb", "imxbRatio"]]
df_l = df_l.rename(columns={"interceptimxb": "intercept", "slopeimxb": "slope", "imxbRatio": "runtime"})

df_b = df_big[["benchmark", "affinity", "interceptimxb", "slopeimxb", "runtime"]]
df_b = df_b.rename(columns={"interceptimxb": "intercept", "slopeimxb": "slope"})

df_cur = pd.concat([df_l, df_b]).sort_index()
df_cur["affinity"] = df_cur.apply(lambda row: "A53" if row["affinity"] == "little" else "A72", axis=1)
df_cur["command"] = df_cur.apply(lambda row: bench_to_cmd[row["benchmark"]], axis=1)

df_cur = df_cur.sort_values(by=["benchmark", "affinity"])
df_cur.to_csv("characteristics-imx8b.csv", index=False)

# tx2 file
df_l = df_little.merge(df_ips, on='benchmark')
df_l = df_l[["benchmark", "affinity", "intercepttx", "slopetx", "txRatio"]]
df_l = df_l.rename(columns={"intercepttx": "intercept", "slopetx": "slope", "txRatio": "runtime"})

df_b = df_big[["benchmark", "affinity", "intercepttx", "slopetx", "runtime"]]
df_b = df_b.rename(columns={"intercepttx": "intercept", "slopetx": "slope"})

df_cur = pd.concat([df_l, df_b]).sort_index()
df_cur["affinity"] = df_cur.apply(lambda row: "A57" if row["affinity"] == "little" else "Denver", axis=1)
df_cur["command"] = df_cur.apply(lambda row: bench_to_cmd[row["benchmark"]], axis=1)

df_cur = df_cur.sort_values(by=["benchmark", "affinity"])
df_cur.to_csv("characteristics-tx2.csv", index=False)