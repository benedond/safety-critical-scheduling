using CSV
using DataFrames
using Gnuplot
using Statistics

dct = Dict()

folder = "../../../experiments/02_linear_regression/measurements/imx8a/"
f_out = "powers_imx8a"
mkdir("./$(f_out)")
for f in readdir(folder)
    if contains(f_out,"imx8")
        df = CSV.read(joinpath(folder,f), DataFrame, comment="#")       
        df = df[df[!,:"time/ms"] .>= 10000.0, :]                
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
        df = CSV.read(joinpath(folder,f), DataFrame, comment="#")       
        df = df[df[!,:"time/ms"] .>= 10000.0, :]        
        df = df[:,["time/ms", "IN_power/mW"]] |> dropmissing        
        dct[f] = std(df[:, "IN_power/mW"])            
        @gp df[:,"time/ms"] df[:,"IN_power/mW"] "with lines title '$(f)'"            
        @gp :- yr=[0,12000] xr=[0,180000] "set grid front"         
        @gp :- "set key noenhanced"
        @gp :- "set xtics rotate by 90"
        save(term="pngcairo size 480,360", output="$(f_out)/$(f).png")
    end
end

vals = sort(collect(dct), by=x->x[2], rev=true)
for i in 1:15
    @info vals[i]
end
