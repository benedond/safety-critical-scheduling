#include <iostream>
#include <fstream>
#include <sstream>

#include "../common/instance.h"
#include "../common/arg_parser.h"
#include "demos_config_writer.h"

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

	environment e;
	task_map t;
	solution s;

	try
	{
		e = parse_environment(json);
		t = parse_tasks(json);
		s = parse_solution(json);
	}
	catch (const nlohmann::detail::parse_error& error)
	{
		std::cerr << "failed to parse input json: " << error.what() << std::endl;
		return EXIT_FAILURE;
	}

	demos_config_writer writer(e, t, s);
	std::string output_string = writer.get_config();

	std::string output_filename = args.get_arg_value("--output");
	if (!output_filename.empty())
	{
		std::ofstream output_file(output_filename);

		if (!output_file.is_open())
		{
			std::cerr << "failed to open output file " << output_filename << std::endl;
			return EXIT_FAILURE;
		}

		output_file << output_string;
	}
	else
	{
		std::cout << output_string;
	}

	return EXIT_SUCCESS;
}
