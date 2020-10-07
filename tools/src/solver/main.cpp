#include <iostream>
#include <fstream>
#include <nlohmann/json.hpp>

#include "simple_solver.h"

#define EXIT_INFEASIBLE_SOLUTION 2

void print_help()
{
	std::cout << "solver help" << std::endl;
}

int main(int argc, char** argv)
{
	std::ifstream* input_file = nullptr;
	std::ofstream* output_file = nullptr;

	for (int i=1; i<argc; i++)
	{
		char* arg = argv[i];
		if (*arg == '-')
			arg++;
		else
			continue;

		char* next_arg = argv[i+1];
		switch (*arg)
		{
			case 'i':
			{
				input_file = new std::ifstream(next_arg);
				if (!input_file->is_open())
				{
					delete input_file;
					std::cerr << "failed to open input file " << next_arg << std::endl;
					return EXIT_FAILURE;
				}

				i++;
				break;
			}

			case 'o':
			{
				output_file = new std::ofstream(next_arg);
				if (!output_file->is_open())
				{
					delete output_file;
					std::cerr << "failed to open output file " << next_arg << std::endl;
					return EXIT_FAILURE;
				}
				i++;
				break;
			}

			case 'h':
			{
				print_help();
				return EXIT_SUCCESS;
			}
		}
	}

	nlohmann::json json;
	Environment environment;
	std::unordered_map<std::string, Task> tasks;

	try
	{
		auto& input_stream = input_file == nullptr ? std::cin : *input_file;
		input_stream >> json;
		environment = parse_environment(json);
		tasks = parse_tasks(json);
		delete input_file;
	}
	catch (const nlohmann::detail::parse_error& error)
	{
		std::cerr << "failed to parse input json: " << error.what() << std::endl;
		return EXIT_FAILURE;
	}

	simple_solver solver(environment, tasks);
	auto solution = solver.get_solution();

	write_solution(json, solution);

	auto& output_stream = output_file == nullptr ? std::cout : *output_file;
	output_stream << json;
	delete output_file;

	return solution.feasible ? EXIT_SUCCESS : EXIT_INFEASIBLE_SOLUTION;
}
