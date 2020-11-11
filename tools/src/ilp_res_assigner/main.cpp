#include <iostream>
#include <chrono>
#include <fstream>
#include <gurobi_c++.h>

#include "../common/instance.h"
#include "../common/arg_parser.h"

#define EXIT_INFEASIBLE_SOLUTION 2
#define INFEASIBLE_MODEL_FILENAME std::string("infeasible_res_assignment.ilp")

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

std::vector<task> solve(const environment& e, const assignment_characteristic_list& assignment_characteristics)
{
    if (e.problem_version != 1)
        throw std::invalid_argument("problem version is not supported");

    std::vector<std::vector<GRBVar>> a;

    GRBEnv env;
    env.set(GRB_IntParam_OutputFlag, 0);
    GRBModel model(env);
    
    for (auto& task : assignment_characteristics)
    {
        std::vector<GRBVar> a_i;
        GRBLinExpr assignment_constraint_expr;

        for (auto& assignment_characteristic : task.resource_assignments)
        {
            GRBVar a_ik = model.addVar(0, 1, assignment_characteristic.energy_consumption, GRB_BINARY);
            assignment_constraint_expr += a_ik;
            a_i.push_back(std::move(a_ik));
        }

        model.addConstr(assignment_constraint_expr == 1);
        a.push_back(std::move(a_i));
    }

    // constraint 3(+4)
    for (auto& processor : e.processors_list)
    {
        GRBLinExpr resource_capacity_contraint_expr;

        int i = 0;
        for (auto& task : assignment_characteristics)
        {
            int k = 0;
            for (auto& assignment_characteristic : task.resource_assignments)
            {
                for (auto& acp : assignment_characteristic.processors)
                {
                    if (acp.processor == processor->name)
                    {
                        resource_capacity_contraint_expr += a[i][k] * acp.processing_units * assignment_characteristic.length;
                    }
                }
                k++;
            }
            i++;
        }

        model.addConstr(resource_capacity_contraint_expr <= e.main_frame_length * processor->processing_units);
    }

    model.optimize();    
    
    std::vector<task> tasks;
    if (model.get(GRB_IntAttr_Status) == GRB_OPTIMAL)
    {
        for (int i = 0; i < assignment_characteristics.size(); i++)
        {
            int used_assignment_ix = 0;
            for (auto& a_ik : a[i])
            {
                if (a_ik.get(GRB_DoubleAttr_X) > 0.5)
                    break;

                used_assignment_ix++;
            }

            auto& t = assignment_characteristics[i];
            auto& c = t.resource_assignments[used_assignment_ix];
            tasks.push_back({ .name = t.task, .length = c.length, .processors = c.processors });
        }
    }
    else
    {
        write_iis(model);
    }

    return tasks;
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
    assignment_characteristic_list assignment_characteristics;
    std::vector<task> tasks;

    try
    {
        environment = parse_environment(json);
        assignment_characteristics = parse_assignment_characteristics(json);
    }
    catch (const nlohmann::detail::parse_error& error)
    {
        std::cerr << "failed to parse input json: " << error.what() << std::endl;
        return EXIT_FAILURE;
    }

    try
    {
        tasks = solve(environment, assignment_characteristics);
        write_tasks(json, tasks);
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

    return !tasks.empty() ? EXIT_SUCCESS : EXIT_INFEASIBLE_SOLUTION;
}