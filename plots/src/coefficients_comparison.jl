
# Compare old and new coefficients measured at imx8(b)

using DataFrames
using CSV
using Gnuplot
using DataFramesMeta

function read_dataframe(file::String)::DataFrame
    return DataFrame(CSV.File(file))
end

function plot_coefficients(old_file::String, new_file::String)
    df_old = read_dataframe(old_file)
    df_new = read_dataframe(new_file)

    df = innerjoin(df_old, df_new, on = [:benchmark, :affinity], makeunique=true)
    
    
    df_A53 = @subset(df, :affinity .== "A53")
    df_A72 = @subset(df, :affinity .== "A72")

    @gp df_A53[!, "slope"] ./ df_A53[!, "slope_1"]  "title 'slope A53 (old/new)'"
    @gp :- df_A53[!, "intercept"] ./ df_A53[!, "intercept_1"]  "title 'intercept A53 (old/new)'"

    @gp :- df_A72[!, "slope"] ./ df_A72[!, "slope_1"]  "title 'slope A72 (old/new)'"
    @gp :- df_A72[!, "intercept"] ./ df_A72[!, "intercept_1"]  "title 'intercept A72 (old/new)'"

    @gp :- "set grid"
    @gp :- xlab="benchmark" ylab="ratio"
end

function plot_runtime(old_file::String, new_file::String)
    df_old = read_dataframe(old_file)
    df_new = read_dataframe(new_file)

    df = innerjoin(df_old, df_new, on = [:benchmark, :affinity], makeunique=true)
    
    
    df_A53 = @subset(df, :affinity .== "A53")
    df_A72 = @subset(df, :affinity .== "A72")

    # normalize to A72
    df_A53[!, "runtime_1"] = df_A53[!, "runtime_1"] ./ df_A72[!, "runtime_1"]
    df_A72[!, "runtime_1"] = df_A72[!, "runtime_1"] ./ df_A72[!, "runtime_1"]

    println(df_A53)

    @gp df_A53[!, "runtime"] ./ df_A53[!, "runtime_1"]  "title 'runtime A53 (old/new)'"    

    # both are one
    # @gp :- df_A72[!, "runtime"] ./ df_A72[!, "runtime_1"]  "title 'runtime A72 (old/new)'"
    @gp :- "set grid"
    @gp :- xlab="benchmark" ylab="ratio"
end


old_file = "./data/characteristics-imx8b-all.csv"
new_file = "./experiments/01_benchmark_coefficients/results/characteristics-imx8b-all.csv"

plot_coefficients(old_file, new_file)
plot_runtime(old_file, new_file)



# df_old = read_dataframe(old_file)
# df_new = read_dataframe(new_file)

# df = innerjoin(df_old, df_new, on = [:benchmark, :affinity], makeunique=true)