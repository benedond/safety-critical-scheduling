# Compare different power models predictions vs. measured values

using DataFrames
using CSV
using Gnuplot

function read_dataframe(file::String)::DataFrame
    df = DataFrame(CSV.File(file))
end

idle_power = Dict("imx8a" => 5.5, "imx8b" => 5.4, "tx2" => 2.6)

# ===================================================

input_path = "../../experiments/power_models_evaluation/results/imx8b-all.csv"
idle = idle_power["imx8b"]

df = read_dataframe(input_path)

df[!, "obj_sm"] .+= idle
df[!, "obj_lr_ub"] .+= idle
df[!, "obj_lr"] .+= idle

# sort df by obj_lr
sort!(df, [:obj_lr])

@gp df[!, "obj_sm"] "title 'SM'"
@gp :- df[!, "obj_lr"] "title 'LR'"
@gp :- df[!, "obj_lr_ub"] "title 'LR-UB'"
@gp :- df[!, "imx8b_power"] "title 'Measured'"
@gp :- xlabel="#instance [-]" ylabel="Power [W]" "set grid" title="Power models estimations and measurements (IMX8b)"

df