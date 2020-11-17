#include <iostream>
#include <chrono>
#include <unordered_map>
#include <fstream>
#include <gurobi_c++.h>

#include "../common/instance.h"
#include "../common/arg_parser.h"

#define EXIT_INFEASIBLE_SOLUTION 2
#define INFEASIBLE_MODEL_FILENAME std::string("infeasible_schedule.ilp")

inline void write_iis(GRBModel& model)
{
    model.computeIIS();

    std::string infeasible_filename(INFEASIBLE_MODEL_FILENAME);

    for (int i = 1; i < 1000; i++)
    {
        std::ifstream file(infeasible_filename);
        if (file.is_open())
        {
            infeasible_filename = INFEASIBLE_MODEL_FILENAME + "." + std::to_string(i);
        }
        else
        {
            file.close();
            model.write(infeasible_filename);
            return;
        }
    }
}

solution solve(const environment& e, const task_map& tasks)
{
    if (e.problem_version != 1)
        throw std::invalid_argument("problem version is not supported");

    std::vector<const task*> task_list;
    task_list.reserve(tasks.size());
    for (auto& t : tasks)
        task_list.push_back(&t.second);

    const int num_tasks = task_list.size();
    const int windows_ub = num_tasks;

    GRBEnv env;
    env.set(GRB_IntParam_OutputFlag, 0);
    GRBModel model(env);
    
    std::vector<std::vector<GRBVar>> w(num_tasks);
    for (int i = 0; i < num_tasks; i++)
    {
        std::vector<GRBVar> w_i(windows_ub);

        GRBLinExpr assignment_constraint;

        for (int j = 0; j < windows_ub; j++)
        {
            w_i[j] = model.addVar(0, 1, 0, GRB_BINARY, "w_" + std::to_string(i) + "," + std::to_string(j));
            assignment_constraint += w_i[j];
        }

        model.addConstr(assignment_constraint == 1);
        w[i] = std::move(w_i);
    }

    std::vector<GRBVar> l(windows_ub);
    GRBLinExpr window_length_sum;
    for (int j = 0; j < windows_ub; j++)
    {
        l[j] = model.addVar(0, GRB_INFINITY, 1, GRB_INTEGER, "l_" + std::to_string(j));
        
        window_length_sum += l[j];

        for (int i = 0; i < num_tasks; i++)
            model.addConstr(l[j] >= (w[i][j] * task_list[i]->length)/0.6);

        if (j > 0)
            model.addConstr(l[j] <= l[j-1]);
    }
    model.addConstr(window_length_sum <= e.major_frame_length);
    
    for (auto& resource : e.processors_list)
    {
        for (int j = 0; j < windows_ub; j++)
        {
            GRBLinExpr resource_capacity_constraint;
            for (int i = 0; i < num_tasks; i++)
            {
                for (auto& processor : task_list[i]->processors)
                {
                    if (processor.processor == resource->name)
                    {
                        resource_capacity_constraint += w[i][j] * processor.processing_units;
                        break;
                    }
                }
            }
            model.addConstr(resource_capacity_constraint <= resource->processing_units);
        }
    }

    auto start = std::chrono::high_resolution_clock::now();
    model.optimize();
    auto end = std::chrono::high_resolution_clock::now();

    solution s { .solver_name = "ILP Solver",
                 .solution_time = (uint64_t) std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() };
    
    if (model.get(GRB_IntAttr_Status) == GRB_OPTIMAL)
    {
        s.feasible = true;

        for (int j = 0; j < windows_ub; j++)
        {
            int window_length = (int) l[j].get(GRB_DoubleAttr_X);
            if (window_length < 1)
                continue;

            std::unordered_map<std::string, int> pu_allocations;
            window win { .length = window_length };
            
            for (int i = 0; i < num_tasks; i++)
            {
                if (w[i][j].get(GRB_DoubleAttr_X) > 0.5)
                {
                    auto t = task_list[i];
                    for (auto& p : t->processors)
                    {
                        win.task_assignments.push_back({ .task = t->name,
                                                         .processor = p.processor,
                                                         .processing_unit = pu_allocations[p.processor],
                                                         .start = 0, .length = t->length });
                        pu_allocations[p.processor] = pu_allocations[p.processor] + 1;
                    }
                }
            }

            s.windows.push_back(std::move(win));
        }
    }
    else
    {
        s.feasible = false;
        write_iis(model);
    }

    return s;
}

int main(int argc, char** argv)
{
    arg_parser args(argc, argv);
    nlohmann::json json;

    std::string input_filename = args.get_arg_value("--input");
    if (!input_filename.empty())
    {
        if (!read_json_from_file(json, input_filename))
            return EXIT_FAILURE;
    }
    else
    {
        std::cin >> json;
    }

    environment environment;
    task_map tasks;

    try
    {
        environment = parse_environment(json);
        tasks = parse_tasks(json);
    }
    catch (const nlohmann::detail::parse_error& error)
    {
        std::cerr << "failed to parse input json: " << error.what() << std::endl;
        return EXIT_FAILURE;
    }

    solution s;
    try
    {
        s = solve(environment, tasks);
        write_solution(json, s);
    }
    catch (const std::invalid_argument& error)
    {
        std::cerr << "argument error: " << error.what() << std::endl;
        return EXIT_FAILURE;
    }

    std::string output_filename = args.get_arg_value("--output");
    if (!output_filename.empty())
    {
        if (!write_json_to_file(json, output_filename))
            return EXIT_FAILURE;
    }
    else
    {
        std::cout << json;
    }

    return s.feasible ? EXIT_SUCCESS : EXIT_INFEASIBLE_SOLUTION;
}
