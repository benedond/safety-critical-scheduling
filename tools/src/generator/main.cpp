#include <iostream>

#include "../common/instance.h"
#include "../common/arg_parser.h"
#include "generator.h"

int main(int argc, char** argv)
{
	arg_parser args(argc, argv);

	nlohmann::json json;

	std::string environment_filename = args.get_arg_value("--environment");
	if (!environment_filename.empty())
	{
		if (!read_json_from_file(json, environment_filename))
			return EXIT_FAILURE;
	}
	else
	{
		std::cin >> json;
	}

	environment environment;
	std::vector<task> tasks;
	try
	{
		environment = parse_environment(json);
		generator g(args, environment);
		tasks = g.generate();
		write_tasks(json, tasks);
	}
	catch (const nlohmann::detail::parse_error& error)
	{
		std::cerr << "failed to parse input json: " << error.what() << std::endl;
		return EXIT_FAILURE;
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

	return EXIT_SUCCESS;
}
