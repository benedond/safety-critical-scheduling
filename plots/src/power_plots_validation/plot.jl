using CSV
using DataFrames
using Gnuplot
using Statistics



to_plot = [
    "../../../experiments/01_benchmark_coefficients/measurements/tx2/" => "01_coef_tx2",
    "../../../experiments/01_benchmark_coefficients/measurements_repeated/tx2/" => "01_coef_tx2_2",
    "../../../experiments/02_linear_regression/measurements/tx2/" => "02_lr_tx2",
    "../../../experiments/02_linear_regression/measurements/imx8a/" => "02_lr_imx8a",
    "../../../experiments/03_power_models_evaluation/measurements/scale-1x/tx2/all" => "03_power_tx2_all",
    "../../../experiments/03_power_models_evaluation/measurements_randomized/scale-1x/tx2/all" => "03_power_tx2_all_rand",
]

for p in to_plot
    folder = p.first
    f_out = p.second
    dct = Dict()
        
    mkpath("./$(f_out)")
    for f in readdir(folder)        
        df = CSV.read(joinpath(folder,f), DataFrame, comment="#")       
        df = df[df[!,:"time/ms"] .>= 10000.0, :]                
        if contains(f_out,"imx8")            
            df = df[:,["time/ms", "energy"]] |> dropmissing        
            # for imx8 -> compute the derivatives
            dt = diff(df[!,"time/ms"])
            derivative = diff(df[!, "energy"]) ./ dt        
            # save stdev
            dct[f] = std(derivative)
            #plot
            @gp df[!,"time/ms"][1:end-1] derivative "with lines title '$(f)'"            
            @gp :- yr=[0,0.05] xr=[0,180000] "set grid front" 
            @gp :- "set key noenhanced"
            @gp :- "set xtics rotate by 90"
            save(term="pngcairo size 480,360", output="$(f_out)/$(f).png")
        else             
            df = df[:,["time/ms", "IN_power/mW"]] |> dropmissing        
            dct[f] = std(df[:, "IN_power/mW"])            
            @gp df[:,"time/ms"] df[:,"IN_power/mW"] "with lines title '$(f)'"            
            @gp :- yr=[0,12000] "set grid front"         
            @gp :- "set key noenhanced"
            @gp :- "set xtics rotate by 90"
            save(term="pngcairo size 480,360", output="$(f_out)/$(f).png")
        end        
    end

    @info folder
    vals = sort(collect(dct), by=x->x[2], rev=true)
    for i in 1:15
        @info vals[i]
    end
    println()
end


