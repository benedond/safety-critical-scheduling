
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

    coeffs = Dict("1" => Dict(), "2" => Dict())
    for (idx, ac) in enumerate(data["assignmentCharacteristics"])
        ra = ac["resourceAssignments"][1]
        coeffs["1"][string(idx)] = Dict("slope" => ra["slope"], "intercept" => ra["intercept"], "length" => ra["length"])
        
        ra = ac["resourceAssignments"][2]
        coeffs["2"][string(idx)] = Dict("slope" => ra["slope"], "intercept" => ra["intercept"], "length" => ra["length"])
    end

    return n_tasks, mf_len, coeffs
end


# Compute the fitnes function of the solution x
function fitness_meta_task(x)
    cluster = collect(map(x -> x == 1 ? n_clusters : 1 + Int(div(x, 1/n_clusters)), x))  # indexed from 1
    window = collect(map(x -> x == 1 ? n_win_ub : 1 + Int(div(x % (1/n_clusters), (1/n_clusters)/n_win_ub)), x))
    window_preference = collect(map( x -> 1 - ((x % (1/n_clusters)) / (1/n_clusters)), x))
    
    window_capacities = [Dict(1 => 4, 2 => 2) for _ in 1:n_win_ub]
    tasks_in_window = [[] for _ in 1:n_win_ub]
    window_lengths = [0 for _ in 1:n_win_ub]

    cur_window = 1
    to_schedule = n_tasks

    for iter in 1:(2*n_win_ub)
        tasks_to_window = findall(window .== cur_window)
        task_idx_sort = sort(tasks_to_window, by=x->window_preference[x], rev=true)  # tasks with maximal preference first

        for t in task_idx_sort
            if window_capacities[cur_window][cluster[t]] > 0 # add the task
                window_capacities[cur_window][cluster[t]] -= 1
                append!(tasks_in_window[cur_window], t)
                to_schedule -= 1
                window[t] = 0  # the task was assigned, "unregister" its window
                window_lengths[cur_window] = max(window_lengths[cur_window], tasks_char[string(cluster[t])][string(t)]["length"])
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

    if to_schedule > 0 # <- the tasks did not fit their clusters
        println("did not fit", to_schedule)
       
    end

    # TODO : compute either sum-max objective or LR objective
    # Compute the objective
    sum_dynamic = [0.0 for _ in 1:n_win_ub]
    max_static = [0.0 for _ in 1:n_win_ub]

    for w in 1:n_win_ub
        for t in tasks_in_window[w]
            t_char = tasks_char[string(cluster[t])][string(t)]
            sum_dynamic[w] += t_char["slope"] * t_char["length"]
            max_static[w] = max(max_static[w], t_char["intercept"])
        end
    end

    obj = sum(sum_dynamic .+ (max_static .* window_lengths)) / major_frame_length                   
     

    constr = [major_frame_length - sum(window_lengths) + 1e6 * (to_schedule)]
    
    return obj, constr, [0.0]

end


function run_meta_task(args)
    bounds = repeat([0 1], n_tasks)
    N_lim = 15*(n_tasks)
    
    solver = WOA(options=Options(debug=true))    
    result = Metaheuristics.optimize(fitness_meta_task, bounds, solver)
    @info "The found solution has objective $(minimum(result))"
    
    # TODO: Write the solution to file.
end

# First parse the arguments
args = parse_commandline()
@info "Parsed command line with args" args

# Load the instance
n_tasks, major_frame_length, tasks_char = load_instance(args["input"])
n_win_ub = n_tasks

# TODO: Load this automatically from the platform file
n_clusters = 2
cores = [4, 2]
slots_per_win = sum(cores)
slot_to_proc = Dict(1 => 1, 2 => 1, 3 => 1, 4 => 1, 5 => 2, 6 => 2)

tasks_lengths = sort([[x["length"] for x in values(tasks_char["1"])] ; [x["length"] for x in values(tasks_char["2"])]])

# Improve the bound on the number of windows in the schedule
n_win_ub = min(findfirst(cumsum(tasks_lengths) .> major_frame_length), n_tasks)
@info "Trying to solve instance with $n_tasks tasks and $n_win_ub windows."

# Run the optimization
run_meta_task(args)