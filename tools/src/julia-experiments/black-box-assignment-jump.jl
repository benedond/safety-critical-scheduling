using JuMP
using NLopt
using JSON
using Metaheuristics

function get_random_char()
    return Dict("slope" => rand(), "intercept" => rand(), "length" => Int(1 + round(10*rand())))
end

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

function feasible(x...)
    indexes = sortperm(collect(x))
    w_len = zeros(n_win_ub)

    for w in 1:n_win_ub
        for s in 1:slots_per_win
            cur_idx = (w-1)*slots_per_win + s
            cur_task = indexes[cur_idx]

            if cur_task > n_tasks  # dummy idle
                continue
            end
            chars = tasks_char[string(slot_to_proc[s])][string(cur_task)]
            w_len[w] = max(w_len[w], chars["length"])
        end
    end                      
    
    if sum(w_len) > major_frame_length
        return 1.0
    else
        return 0.0
    end

    return max(0, sum(w_len) - major_frame_length)
end

function fitness(x...)
    indexes = sortperm(collect(x))
    w_len = zeros(n_win_ub)
    sum_dynamic = zeros(n_win_ub)
    max_static = zeros(n_win_ub)

    for w in 1:n_win_ub
        for s in 1:slots_per_win
            cur_idx = (w-1)*slots_per_win + s
            cur_task = indexes[cur_idx]

            if cur_task > n_tasks  # dummy idle
                continue
            end
            chars = tasks_char[string(slot_to_proc[s])][string(cur_task)]
            sum_dynamic[w] += chars["slope"] * chars["length"]
            max_static[w] = max(max_static[w], chars["intercept"])
            w_len[w] = max(w_len[w], chars["length"])
        end
    end        

    obj = sum(sum_dynamic .+ (max_static .* w_len)) / major_frame_length                   
    
    if sum(w_len) > major_frame_length
        return 1e4 + obj
    end
    return obj

end


function fitness_meta(x)
    indexes = sortperm(collect(x))
    w_len = zeros(n_win_ub)
    sum_dynamic = zeros(n_win_ub)
    max_static = zeros(n_win_ub)

    for w in 1:n_win_ub
        for s in 1:slots_per_win
            cur_idx = (w-1)*slots_per_win + s
            cur_task = indexes[cur_idx]

            if cur_task > n_tasks  # dummy idle
                continue
            end
            chars = tasks_char[string(slot_to_proc[s])][string(cur_task)]
            sum_dynamic[w] += chars["slope"] * chars["length"]
            max_static[w] = max(max_static[w], chars["intercept"])
            w_len[w] = max(w_len[w], chars["length"])
        end
    end        

    obj = sum(sum_dynamic .+ (max_static .* w_len)) / major_frame_length                   
    
    constr = [major_frame_length - sum(w_len)]
    
    return obj, constr, [0.0]

end

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

function run()
    model = Model(NLopt.Optimizer)
    set_optimizer_attribute(model, "maxtime", 10)

    @variable(model, 0 <= x[1:n_win_ub*slots_per_win] <= 1)

    register(model, :fitness, n_win_ub*slots_per_win, fitness; autodiff = true)
    @NLobjective(model, Min, fitness(x...))
    #register(model, :feasible, n_win_ub*slots_per_win, feasible; autodiff = true)
    #@NLconstraint(model, feasible(x...) == 0)

    for i in 1:n_win_ub*slots_per_win
        set_start_value(x[i], 0.5)
    end

    # GN_ISRES supports constrains, 
    # ESCH looked relatively good (performed better on unconstrained problem)
    set_optimizer_attribute(model, "algorithm", :GN_ESCH) 
    #set_optimizer_attribute(model, "algorithm", :GN_ISRES) 

    JuMP.optimize!(model)
    println("got ", objective_value(model))  # " at ", value.(x)
end

function run_meta()
    bounds = repeat([0 1], slots_per_win*n_win_ub)
    N_lim = 15*(slots_per_win*n_win_ub)
    
    solver = ECA(N=N_lim, options=Options(debug=true))
    #solver = PSO(N=N_lim, options=Options(debug=true))
    #solver = ABC(N=N_lim, options=Options(debug=true))
    #solver = CGSA(N=N_lim, options=Options(debug=true))  # seems rather promising
    #solver = SA(options=Options(debug=true))  # even better
    #solver = SPEA2(N=N_lim, options=Options(debug=true)) 
    
    #result = Metaheuristics.optimize(x -> fitness(x...), bounds, solver)
    result = Metaheuristics.optimize(fitness_meta, bounds, solver)
    println("Minimum:", " ", minimum(result))
end

function run_meta_task()
    bounds = repeat([0 1], n_tasks)
    N_lim = 15*(n_tasks)
    
    #solver = ECA(N=N_lim, options=Options(debug=true))
    #solver = PSO(N=N_lim, options=Options(debug=true))
    #solver = CGSA(N=N_lim, options=Options(debug=true))  # seems rather promising
    #solver = SA(options=Options(debug=true, iterations=1000000))  # even better
    solver = WOA(options=Options(debug=true))  # even better
    
    result = Metaheuristics.optimize(fitness_meta_task, bounds, solver)
    println("Minimum:", " ", minimum(result))
end

input_path = "instnces/11_6_1.json"
#input_path = "instnces/IN_50.json"


n_tasks, major_frame_length, tasks_char = load_instance(input_path)
n_win_ub = n_tasks
n_clusters = 2
cores = [4, 2]
slots_per_win = sum(cores)
slot_to_proc = Dict(1 => 1, 2 => 1, 3 => 1, 4 => 1, 5 => 2, 6 => 2)

tasks_lengths = sort([[x["length"] for x in values(tasks_char["1"])] ; [x["length"] for x in values(tasks_char["2"])]])


n_win_ub = min(findfirst(cumsum(tasks_lengths) .> major_frame_length), n_tasks)
println(n_tasks, " ", n_win_ub)

# tasks_char = JSON.parsefile("data.json")

println("Optimize by meta-task")
for i in 1:2
    run_meta_task()
end

println("Optimize by meta")
for i in 1:2
    run_meta()
end

println("Optimizing by NLopt.")
for i in 1:2
    run()
end


open("data.json","w") do f 
    JSON.print(f, tasks_char)
end