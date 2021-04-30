#include <iostream>

#include "../common/instance.h"
#include "../common/arg_parser.h"
#include "../common/ilp_util.h"
#include "ilp_global_solver.h"

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

	bool solution_feasible = false;
	try
	{
		environment = parse_environment(json);
		assignment_characteristics = parse_assignment_characteristics(json);
	}
	catch (const nlohmann::detail::parse_error & error)
	{
		std::cerr << "failed to parse input json: " << error.what() << std::endl;
		return EXIT_FAILURE;
	}

	try
	{
		auto sol = solve(args, environment, assignment_characteristics);
		write_tasks(json, sol.second);
		write_solution(json, sol.first);
		solution_feasible = sol.first.feasible;
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

	return solution_feasible ? EXIT_SUCCESS : EXIT_INFEASIBLE_SOLUTION;
}