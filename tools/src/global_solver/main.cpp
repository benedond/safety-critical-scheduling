#include <iostream>

#include "../common/arg_parser.h"
#include "random_global_solver.h"

#define EXIT_INFEASIBLE_SOLUTION 2

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
	assignment_characteristic_list assignments;

	try
	{
		environment = parse_environment(json);
		assignments = parse_assignment_characteristics(json);
	}
	catch (const nlohmann::detail::parse_error& error)
	{
		std::cerr << "failed to parse input json: " << error.what() << std::endl;
		return EXIT_FAILURE;
	}

	solution s;
	try
	{
		random_global_solver solver(environment, assignments);
		s = solver.get_solution();
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
