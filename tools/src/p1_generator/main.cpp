#include <iostream>
#include <fstream>

#include "../common/instance.h"
#include "../common/arg_parser.h"
#include "p1_generator.h"

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

	std::string benchmark_data_filename = args.get_arg_value("--benchmark-data");
	if (benchmark_data_filename.empty())
	{
		std::cerr << "unable to continue: no benchmark data provided" << std::endl;
		return EXIT_FAILURE;
	}

	std::ifstream benchmark_data_file(benchmark_data_filename);
	if (!benchmark_data_file.is_open())
	{
		std::cerr << "unable to continue: cannot open benchmark data file" << std::endl;
		return EXIT_FAILURE;
	}

	environment environment;
	std::vector<assignment_characteristic> tasks;
	try
	{
		environment = parse_environment(json);
		auto benchmark_data = parse_benchmark_data(environment.processors, benchmark_data_file);
		p1_generator g(args, environment, benchmark_data);
		tasks = g.generate();
		write_assignment_characteristics(json, tasks);

		if (!args.is_arg_present("--keep-environment-mf"))
		{
			json["environment"]["majorFrameLength"] = compute_major_frame_length(tasks);
		}
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
