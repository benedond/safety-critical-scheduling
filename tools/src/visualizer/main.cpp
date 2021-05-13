#include <iostream>

#include "../common/instance.h"
#include "../common/arg_parser.h"
#include "visualizer.h"

int main(int argc, char** argv)
{
	arg_parser args(argc, argv);

	bool display_visualization = args.is_arg_present("--display");
	std::string output_filename = args.get_arg_value("--output");

	if (!display_visualization && output_filename.empty())
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

	visualizer v(environment, solution);

	if (!output_filename.empty())
	{
		if (output_filename.size() < 5)
		{
			std::cerr << "output filename error" << std::endl;
		}
		else
		{
			auto format = output_filename.substr(output_filename.size()-4, output_filename.size()-1);

			if (format == ".bmp")
				v.export_bmp(output_filename);
			else if (format == ".png")
				v.export_png(output_filename);
			else
				std::cerr << "output error: unsupported format" << std::endl;
		}
	}

	if (display_visualization)
		v.display();

	return EXIT_SUCCESS;
}