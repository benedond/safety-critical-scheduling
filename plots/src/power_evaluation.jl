# Compare different power models predictions vs. measured values

using DataFrames
using CSV
using Gnuplot

function read_dataframe(file::String)::DataFrame
    df = DataFrame(CSV.File(file))
end

idle_power = Dict("imx8a" => 5.5, "imx8b" => 5.4, "tx2" => 2.6)

function plot(input_path, platform, name)
    idle = idle_power[platform]
    df = read_dataframe(input_path)
    
    df[!, "obj_sm"] .+= idle
    df[!, "obj_lr_ub"] .+= idle
    df[!, "obj_lr"] .+= idle
    
    # sort df by obj_lr
    #sort!(df, [:obj_lr])
    #sort!(df, [:obj_sm])
    sort!(df, [:power])
    
    @gp df[!, "obj_sm"] "title 'SM'"
    @gp :- df[!, "obj_lr"] "title 'LR'"
    @gp :- df[!, "obj_lr_ub"] "title 'LR-UB'"
    @gp :- df[!, "power"] "title 'Measured'"
    @gp :- xlabel="#instance [-]" ylabel="Power [W]" "set grid" title="Power models estimations and measurements ($(name))"
    save(term="pngcairo size 1280,960 noenhanced", output="../bin/power_evaluation/$(name).png")    
    
    @gp :-
end

function plot_relative(input_path, platform, name)
    idle = idle_power[platform]
    df = read_dataframe(input_path)
    
    df[!, "obj_sm"] .+= idle
    df[!, "obj_lr_ub"] .+= idle
    df[!, "obj_lr"] .+= idle
    
    # sort df by obj_lr
    sort!(df, [:obj_lr])
    #sort!(df, [:obj_sm])
    #sort!(df, [:power])
    
    @gp df[!, "obj_sm"] ./ df[!, "power"] "title 'SM'"
    @gp :- df[!, "obj_lr"] ./ df[!, "power"] "title 'LR'"
    @gp :- df[!, "obj_lr_ub"] ./ df[!, "power"] "title 'LR-UB'"
    @gp :- df[!, "power"] ./ df[!, "power"] "title 'Measured'"
    @gp :- xlabel="#instance [-]" ylabel="Relative power [-]" "set grid" title="Power models estimations and measurements ($(name))"
    save(term="pngcairo size 1280,960 noenhanced", output="../bin/power_evaluation/$(name).png")    
    
    @gp :-
end

# ===================================================

plot("../../experiments/01_power_models_evaluation/results/scale-1x-imx8a-all.csv", "imx8a", "power_imx8a_all")
plot("../../experiments/01_power_models_evaluation/results/scale-1x-imx8a-cpu.csv", "imx8a", "power_imx8a_cpu")

plot("../../experiments/01_power_models_evaluation/results/scale-1x-imx8b-all.csv", "imx8b", "power_imx8b_all")
plot("../../experiments/01_power_models_evaluation/results/scale-1x-imx8b-cpu.csv", "imx8b", "power_imx8b_cpu")

plot("../../experiments/01_power_models_evaluation/results/scale-3x-imx8b-all.csv", "imx8b", "power_3x_imx8b_all")
plot("../../experiments/01_power_models_evaluation/results/scale-3x-imx8b-cpu.csv", "imx8b", "power_3X_imx8b_cpu")

plot("../../experiments/01_power_models_evaluation/results/scale-1x-imx8b-all-30.csv", "imx8b", "power_imx8b_all_30s")
plot("../../experiments/01_power_models_evaluation/results/scale-1x-imx8b-cpu-30.csv", "imx8b", "power_imx8b_cpu_30s")


plot_relative("../../experiments/01_power_models_evaluation/results/scale-1x-imx8a-all.csv", "imx8a", "relative_power_imx8a_all")
plot_relative("../../experiments/01_power_models_evaluation/results/scale-1x-imx8a-cpu.csv", "imx8a", "relative_power_imx8a_cpu")

plot_relative("../../experiments/01_power_models_evaluation/results/scale-1x-imx8b-all.csv", "imx8b", "relative_power_imx8b_all")
plot_relative("../../experiments/01_power_models_evaluation/results/scale-1x-imx8b-cpu.csv", "imx8b", "relative_power_imx8b_cpu")


plot_relative("../../experiments/01_power_models_evaluation/results/scale-3x-imx8b-all.csv", "imx8b", "relative_power_3x_imx8b_all")
plot_relative("../../experiments/01_power_models_evaluation/results/scale-3x-imx8b-cpu.csv", "imx8b", "relative_power_3x_imx8b_cpu")


plot_relative("../../experiments/01_power_models_evaluation/results/scale-1x-imx8b-all-30.csv", "imx8b", "relative_power_imx8b_all_30s")
plot_relative("../../experiments/01_power_models_evaluation/results/scale-1x-imx8b-cpu-30.csv", "imx8b", "relative_power_imx8b_cpu_30s")