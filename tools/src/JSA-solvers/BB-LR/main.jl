using ArgParse
using JuMP
using NLopt
using JSON
using Metaheuristics

function parse_commandline()
    s = ArgParseSettings()
    @add_arg_table s begin
        "--input", "-i"
            help = "Path to the input file"
            arg_type = String
            required = true            
        "--output", "-o"
            help = "Path to the output file"
            arg_type = String
            required = true
        "--timelimit", "-t"
            help = "Timelimit in seconds"            
            arg_type = Float64
            default = 60.0
        "--path_lr", "-c"
            help = "Path to the LR coefficients file"
            arg_type = String
            required = true
        "--platform", "-p"
            help = "Platform, [imx8a, imx8b, tx2]"
            required = true
            range_tester = (x->x ∈ ["imx8a", "imx8b", "tx2"])
        "--model", "-m"
            help = "Power model to be used for fitness evaluation [sm, lr]; sm for sum-max, lr for linear regression."
            required = true
            range_tester = (x->x ∈ ["sm", "lr"])
    end
    return parse_args(s)
end


# Given path to the instance file, load 
# - number of tasks
# - length of the major frame
# - tasks coefficients (slope, intercept, length)
function load_instance(path)
    data = JSON.parsefile(path)
    
    n_tasks = length(data["assignmentCharacteristics"])
    mf_len = data["environment"]["majorFrameLength"]
    
    coeffs = Dict(p["name"] => Dict()  for p in data["environment"]["processors"])
    
    for (idx, ac) in enumerate(data["assignmentCharacteristics"])  # tasks
        # Write the coeffisients for each assignment of this task
        for ra in ac["resourceAssignments"]  # Assume that each assignment is only to a single processor (i.e., cluster)
            coeffs[ra["processors"][1]["processor"]][idx] = Dict("slope" => ra["slope"], "intercept" => ra["intercept"], "length" => ra["length"])
        end

        # The solver assumes that each task can be assigned to each of the available processors
        for proc in keys(coeffs)
            if !haskey(coeffs[proc], idx)
                error("The solver assumes that each task can be assigned to each of the available processors,
                 but task with index $(idx) does not have characteristics for processor $(proc).")
            end
        end
    end

    return n_tasks, mf_len, coeffs
end

# Load environment from the instance file
function load_environment(path)
    data = JSON.parsefile(path)

    clusters = [p["name"] for p in data["environment"]["processors"]]
    cores = [length(p["coreIds"]) for p in data["environment"]["processors"]]
    env = data["environment"]

    return clusters, cores, env
end

function load_lr_coeffs(path, platform)
    data = JSON.parsefile(path)
    return data[platform]
end

# based on real-valued vector x, compute task-to-processor and task-to-window assingments
# return task_to_cluster, tasks_in_window and window_lengths, to_schedule (no of remaining tasks)
function assign_tasks(x)
    cluster = collect(map(x -> x == 1 ? n_clusters : 1 + Int(div(x, 1/n_clusters)), x))  # indexed from 1
    window = collect(map(x -> x == 1 ? n_win_ub : 1 + Int(div(x % (1/n_clusters), (1/n_clusters)/n_win_ub)), x))
    window_preference = collect(map( x -> 1 - ((x % (1/n_clusters)) / (1/n_clusters)), x))
    
    window_capacities = [Dict(i => cores[i] for i in 1:length(cores)) for _ in 1:n_win_ub]
    tasks_in_window = [[] for _ in 1:n_win_ub]
    window_lengths = [0 for _ in 1:n_win_ub]

    cur_window = 1
    to_schedule = n_tasks

    for iter in 1:(2*n_win_ub) # Iterate twice (the tasks from the last windows are shifted to the beginning)
        tasks_to_window = findall(window .== cur_window)
        task_idx_sort = sort(tasks_to_window, by=x->window_preference[x], rev=true)  # tasks with maximal preference first

        for t in task_idx_sort
            if window_capacities[cur_window][cluster[t]] > 0 # add the task
                window_capacities[cur_window][cluster[t]] -= 1
                append!(tasks_in_window[cur_window], t)
                to_schedule -= 1
                window[t] = 0  # the task was assigned, "unregister" its window
                window_lengths[cur_window] = max(window_lengths[cur_window], tasks_char[clusters[cluster[t]]][t]["length"])
            else  # skip the task, and increase its preference
                window[t] = cur_window == n_win_ub ? 1 : (cur_window + 1)
                window_preference[t] = 1  # maximize the preference (the task was delayed to next window)
            end
        end

        cur_window = cur_window == n_win_ub ? 1 : (cur_window + 1)
        if to_schedule < 1
            break
        end
    end

    return cluster, tasks_in_window, window_lengths, to_schedule
end


function compute_obj_sum_max(cluster, tasks_in_window, window_lengths)
    # Compute the objective
    sum_dynamic = [0.0 for _ in 1:n_win_ub]
    max_static = [0.0 for _ in 1:n_win_ub]

    for w in 1:n_win_ub
        for t in tasks_in_window[w]
            t_char = tasks_char[clusters[cluster[t]]][t]
            sum_dynamic[w] += t_char["slope"] * t_char["length"]
            max_static[w] = max(max_static[w], t_char["intercept"])
        end
    end

    obj = sum(sum_dynamic .+ (max_static .* window_lengths)) / major_frame_length                   
    return obj
end

function compute_obj_lr(cluster, tasks_in_window)
    obj = 0

    for w in 1:n_win_ub
        cur_lengths = [tasks_char[clusters[cluster[t]]][t]["length"] for t in tasks_in_window[w]]
        sort!(cur_lengths)
        start = 0

        for l in cur_lengths
            features = Dict(clusters[c] => Dict("slope" => 0.0, "intercept" => 0.0) for c in [1,2])

            for t in tasks_in_window[w]
                t_char = tasks_char[clusters[cluster[t]]][t]
                if t_char["length"] > start
                    features[clusters[cluster[t]]]["slope"] += t_char["slope"]
                    features[clusters[cluster[t]]]["intercept"] += t_char["intercept"]
                end
            end

            obj += (features[clusters[1]]["slope"] * lr_coeffs[clusters[1]]["slope"] + 
                    features[clusters[1]]["intercept"] * lr_coeffs[clusters[1]]["intercept"] + 
                    features[clusters[2]]["slope"] * lr_coeffs[clusters[2]]["slope"] + 
                    features[clusters[2]]["intercept"] * lr_coeffs[clusters[2]]["intercept"]) * (l - start)

            start = l
        end
    end
    return obj / major_frame_length
end

# Compute the fitnes function of the solution x
function fitness_meta_task(x)
    cluster, tasks_in_window, window_lengths, to_schedule = assign_tasks(x)
    
    # Compute objective
    if args["model"] == "sm"
        obj = compute_obj_sum_max(cluster, tasks_in_window, window_lengths)
    elseif args["model"] == "lr"
        obj = compute_obj_lr(cluster, tasks_in_window)
    else
        # Unknown modle, use sm by default
        @warn "Unknown model $(args["model"]) was used; using sm by default"
        obj = compute_obj_sum_max(cluster, tasks_in_window, window_lengths)
    end

    constr = [major_frame_length - sum(window_lengths) + 1e6 * (to_schedule)]
    return obj, constr, [0.0]
end


function run_meta_task()
    bounds = repeat([0 1], n_tasks)
    best_result = missing
    best_obj = Inf64
    remaining_time = time_limit_sec
    
    while true
        t_sec = @elapsed begin
            @info "Iterating WOA; remaining time $(remaining_time), sol $(best_obj)"
            solver = WOA(N=1*n_tasks, options=Options(debug=false, time_limit=remaining_time))    
            result = Metaheuristics.optimize(fitness_meta_task, bounds, solver)
        end

        if minimum(result) <= best_obj
            best_obj = minimum(result)
            best_result = result
        end

        remaining_time -= t_sec
    
        if remaining_time <= 0
            break
        end
    end
    @info "The found solution has objective $(minimum(best_result))"
    
    # TODO: Write the solution to file.
end

# First parse the arguments
args = parse_commandline()
@info "Parsed command line with args" args

in_path = args["input"]
lr_path = args["path_lr"]
args_platform = args["platform"]
time_limit_sec = args["timelimit"]

#in_path = "./instances/IN_1_imx8a.json"
#lr_path = "../../../../data/LR-coefficients.json"
#args_platform = "imx8a"

# Load the instance
n_tasks, major_frame_length, tasks_char = load_instance(in_path)
clusters, cores, env = load_environment(in_path)
n_clusters = length(clusters)
lr_coeffs = load_lr_coeffs(lr_path, args_platform)

# Compute the upper bound on the number of windows (each window for one task 
# - start from the shortest one, end when MF is reached)
tasks_lengths = sort([min(x["length"],y["length"]) for (x,y) in zip(values(tasks_char[clusters[1]]), values(tasks_char[clusters[2]]))])
n_win_ub = min(findfirst(cumsum(tasks_lengths) .> major_frame_length), n_tasks)
@info "Trying to solve instance with $n_tasks tasks and $n_win_ub windows."

# ILP-SM-1 solution to IN_1_imx8a
# x = [rand() for _ in 1:n_tasks]
# x[3] = 0
# x[4] = 0
# x[7] = 0
# x[19] = 0
# x[5] = 0.5
# -- next window
# x[6] = (0.5/n_win_ub) * 1
# x[8] = (0.5/n_win_ub) * 1
# x[17] =  (0.5/n_win_ub) * 1
# x[18] = (0.5/n_win_ub) * 1
# -- next window
# x[9] = (0.5/n_win_ub) * 2
# x[11] = (0.5/n_win_ub) * 2
# x[15] =  (0.5/n_win_ub) * 2
# x[20] = (0.5/n_win_ub) * 2
# x[10] = 0.5 + (0.5/n_win_ub) * 2
# x[14] = 0.5 + (0.5/n_win_ub) * 2
# -- next window
# x[1] = (0.5/n_win_ub) * 3
# x[2] = (0.5/n_win_ub) * 3
# x[13] =  (0.5/n_win_ub) * 3
# x[16] = (0.5/n_win_ub) * 3
# x[12] = 0.5 + (0.5/n_win_ub) * 3
# @info fitness_meta_task(x)

# Run the optimization
run_meta_task()