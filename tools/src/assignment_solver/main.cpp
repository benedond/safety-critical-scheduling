#include <iostream>

#include "../common/instance.h"
#include "../common/arg_parser.h"
#include "../common/ilp_util.h"
#include "assignment_solver.h"

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
    	if (args.is_arg_present("--method"))
		{
    		auto method = args.get_arg_value("--method");

    		if (method == "reference") tasks = solve_reference(args, environment, assignment_characteristics);
    		else if (method == "utilization") tasks = solve_utilization(args, environment, assignment_characteristics);
    		else if (method == "random") tasks = solver_random(args, environment, assignment_characteristics);
    		else if (method == "old") tasks = solve_old(args, environment, assignment_characteristics, assignment_cuts);
		}
    	else tasks = solve_reference(args, environment, assignment_characteristics);

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
