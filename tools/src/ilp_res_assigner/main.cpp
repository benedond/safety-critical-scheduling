#include <iostream>
#include <chrono>
#include <fstream>
#include <gurobi_c++.h>

#include "../common/instance.h"
#include "../common/arg_parser.h"
#include "../common/ilp_util.h"

#define INFEASIBLE_MODEL_FILENAME std::string("infeasible_res_assignment")

std::vector<task> solve(const arg_parser& args, const environment& e, const assignment_characteristic_list& assignment_characteristics, const assignment_cut_list& assignment_cuts)
{
    if (e.problem_version != 1)
        throw std::invalid_argument("problem version is not supported");

    std::vector<std::vector<GRBVar>> a;
    std::unordered_map<std::string, int> task_index_map;

    GRBEnv env;
    GRBModel model(env);

    int ix = 0;
    for (auto& task : assignment_characteristics)
    {
        task_index_map[task.task] = ix++;

        std::vector<GRBVar> a_i;
        GRBLinExpr assignment_constraint_expr;

        for (auto& assignment_characteristic : task.resource_assignments)
        {
            int processor_capacity = 0;
            for (auto& p : assignment_characteristic.processors)
                processor_capacity += e.processors.at(p.processor).processing_units;
            float energy_consumption = assignment_characteristic.slope + (float)assignment_characteristic.intercept / (float)processor_capacity;

            GRBVar a_ik = model.addVar(0, 1, energy_consumption, GRB_BINARY, "a" + std::to_string(ix - 1) + "," + std::to_string(a_i.size()));
            assignment_constraint_expr += a_ik;
            a_i.push_back(std::move(a_ik));
        }

        model.addConstr(assignment_constraint_expr == 1, task.task + " assigned");
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

        model.addConstr(resource_capacity_contraint_expr <= e.major_frame_length * processor->processing_units, processor->name + " capacity (relaxed)");
    }

    for (auto& assignment_cut : assignment_cuts)
    {
        GRBLinExpr assignment_cut_constraint;

        for (auto& assignment : assignment_cut)
        {
            int task_index = task_index_map[assignment.task];
            assignment_cut_constraint += a[task_index][assignment.assignment_index];
        }

        model.addConstr(assignment_cut_constraint <= assignment_cut.size() - 1, "assignment cut");
    }

    model.optimize();

    std::vector<task> tasks;
    if (model.get(GRB_IntAttr_Status) == GRB_OPTIMAL || model.get(GRB_IntAttr_Status) == GRB_TIME_LIMIT)
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
            tasks.push_back({ .name = t.task, .command = t.command, .length = c.length, .assignment_index = used_assignment_ix, .processors = c.processors });
        }
    }
    else
    {
        bool iis_output = !args.is_arg_present("--no-iis-output");
        if (iis_output)
        {
            model.computeIIS();
            write_iis(INFEASIBLE_MODEL_FILENAME, model);
        }
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
    assignment_cut_list assignment_cuts;
    std::vector<task> tasks;

    try
    {
        environment = parse_environment(json);
        assignment_characteristics = parse_assignment_characteristics(json);
        assignment_cuts = parse_assignment_cuts(json);
    }
    catch (const nlohmann::detail::parse_error & error)
    {
        std::cerr << "failed to parse input json: " << error.what() << std::endl;
        return EXIT_FAILURE;
    }

    try
    {
        tasks = solve(args, environment, assignment_characteristics, assignment_cuts);
        write_tasks(json, tasks);
    }
    catch (const std::invalid_argument & error)
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
