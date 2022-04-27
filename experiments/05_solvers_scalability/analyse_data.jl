using DataFrames
using CSV
using DataFramesMeta
using Measurements
using Statistics
using Plots
pgfplotsx()


function analze_data(in_path::String, out_path::Union{String,Nothing}, func=median, logplot::Bool=false)
    df = DataFrame(CSV.File(in_path))

    solvers = unique(df.:solver)
    sizes = sort(unique(df.:n))
    data = Dict(n => Dict(s => Inf64 ± Inf64 for s in solvers) for n in sizes)
    timelimit = 300
    
    for s in solvers
        for n in sizes
            df_cur = @subset(df, :solver .== s, :n .== n)          
            data[n][s] = min(func(df_cur.:time)/1000, timelimit)
            #data[n][s] = func(df_cur.:obj_sm)
        end
    end
    
    fig = nothing
    begin # Plot
        if logplot
            fig = plot(legend=:topleft, yticks = [1e-4, 1e-2, 1e0, 1e2], yaxis=:log)
        else
            fig = plot(legend=:topleft)
        end
        data_solvers = Dict(s => [data[n][s] for n in sizes] for s in solvers)
        for s in solvers            
            plot!(sizes, data_solvers[s], label=s, markerstrokecolor=:auto)
        end
        xlabel!("Instance size [-]")
        ylabel!("Time [s]")
    end
    
    if !isnothing(out_path)
        savefig("$(out_path).pdf")
        savefig("$(out_path).tex")        
    end

    return (df, fig)
end

(df, fig) = analze_data("./experiments/21_JSA_experiments/results/scalability-imx8a.csv", "log_plot_scalability")
@show fig

(df, fig) = analze_data("./experiments/21_JSA_experiments/results/scalability_ilp-imx8a.csv", "log_scalability_ilp")
@show fig

(df, fig) = analze_data("./experiments/21_JSA_experiments/results/scalability_ilp_20-36-imx8a.csv", "ilp_time", mean)
@show fig


begin # Fill in relative improvement
    instances = sort(unique(df.:instance))
    sm2_res = Dict()
    for inst in instances
        obj_ref = @subset(df, :solver .== "ILP-SM-II", :instance .== inst)[!,"obj_sm"][1]
        sm2_res[inst] = obj_ref
    end
    
    get_id(inst) = parse(Int, split(inst, "_")[end])
    get_relative(obj,inst) = obj / sm2_res[inst]
    @transform!(df, :idx = get_id.(:instance))
    @transform!(df, :obj_rel = get_relative.(:obj_sm,:instance))

    df_cur =  @subset(df, :solver .== "ILP-SM-I")
    scatter(df_cur[!,:n], df_cur[!,:obj_rel], m=:x, xlabel="Instance size [-]", ylabel="Relative improvement [-]", label=nothing)
    savefig("relative_improvement.pdf")
    savefig("relative_improvement.tex")  
end
