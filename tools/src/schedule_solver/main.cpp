#include <iostream>

#include "../common/arg_parser.h"
#include "longest_tasks_first_solver.h"
#include "random_task_order_solver.h"

#define EXIT_INFEASIBLE_SOLUTION 2

enum solvers
{
	longest_tasks_first,
	random_task_order,
};

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
		std::unique_ptr<solver> solver;
		int method = 0;
		args.set_arg_value_int("--method", &method);

		switch (method)
		{
			default:
			case longest_tasks_first:
				solver = std::make_unique<longest_tasks_first_solver>(environment, tasks);
				break;

			case random_task_order:
				solver = std::make_unique<random_task_order_solver>(environment, tasks);
				break;
		}

		s = solver->get_solution();

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
