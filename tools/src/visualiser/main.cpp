#include <iostream>

#include "../common/instance.h"
#include "../common/arg_parser.h"
#include "visualiser.h"

int main(int argc, char** argv)
{
	arg_parser args(argc, argv);

	bool display_visualisation = args.is_arg_present("--display");
	std::string output_filename = args.get_arg_value("--output");

	if (!display_visualisation && output_filename.empty())
	{
		std::cerr << "nothing to do" << std::endl;
		return EXIT_SUCCESS;
	}

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
	solution solution;

	try
	{
		environment = parse_environment(json);
		solution = parse_solution(json);
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

	visualiser v(environment, solution);

	if (!output_filename.empty())
		v.export_bmp(output_filename);

	if (display_visualisation)
		v.display();

	return EXIT_SUCCESS;
}