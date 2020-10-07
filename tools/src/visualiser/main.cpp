#include <iostream>
#include <fstream>

#include "../common/instance.h"
#include "visualiser.h"

void print_help()
{
	std::cout << "visualiser help" << std::endl;
}

int main(int argc, char** argv)
{
	std::ifstream* input_file = nullptr;
	bool display_visualisation = false;
	std::string output_filename;

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
				output_filename.append(next_arg);
				i++;
				break;
			}

			case 'd':
			{
				display_visualisation = true;
				break;
			}

			case 'h':
			{
				print_help();
				return EXIT_SUCCESS;
			}
		}
	}

	if (!display_visualisation && output_filename.empty())
	{
		std::cerr << "nothing to do" << std::endl;
		return EXIT_FAILURE;
	}

	nlohmann::json json;
	environment environment;
	solution solution;

	try
	{
		auto& input_stream = input_file == nullptr ? std::cin : *input_file;
		input_stream >> json;
		environment = parse_environment(json);
		solution = parse_solution(json);
		delete input_file;
	}
	catch (const nlohmann::detail::parse_error& error)
	{
		std::cerr << "failed to parse input json: " << error.what() << std::endl;
		return EXIT_FAILURE;
	}

	visualiser v(environment, solution);

	if (!output_filename.empty())
		v.export_bmp(output_filename);

	if (display_visualisation)
		v.display();

	return EXIT_SUCCESS;
}