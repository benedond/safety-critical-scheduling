#include <iostream>
#include <fstream>
#include <sstream>

#include "../common/instance.h"
#include "../common/arg_parser.h"

#define CSV_SEPARATOR ";"
#define NEWLINE "\n"

const static std::string csv_header = "file"
									  CSV_SEPARATOR
									  "problem_version"
									  CSV_SEPARATOR
									  "solver"
									  CSV_SEPARATOR
									  "solve_time"
									  CSV_SEPARATOR
									  "window_length_sum"
									  NEWLINE;

int compute_window_length_sum(const solution& s)
{
	int window_length_sum = 0;

	if (s.feasible)
		for (auto& w : s.windows)
			window_length_sum += w.length;

	return window_length_sum;
}

int main(int argc, char** argv)
{
	arg_parser args(argc, argv);

	nlohmann::json json;
	bool no_input = args.is_arg_present("--no-input");

	std::string input_filename;
	if (!no_input)
	{
		input_filename = args.get_arg_value("--input");
		if (!input_filename.empty())
			no_input = !read_json_from_file(json, input_filename);
		else
			std::cin >> json;
	}

	std::stringstream output;
	if (args.is_arg_present("--write-header"))
		output << csv_header;

	if (!no_input)
	{
		environment e;
		solution s;
		try
		{
			e = parse_environment(json);
			s = parse_solution(json);
		}
		catch (const nlohmann::detail::parse_error& error)
		{
			std::cerr << "failed to parse input json: " << error.what() << std::endl;
			return EXIT_FAILURE;
		}

		output << input_filename << CSV_SEPARATOR;
		output << e.problem_version << CSV_SEPARATOR;
		output << s.solver_name << CSV_SEPARATOR;
		output << s.solution_time << CSV_SEPARATOR;
		output << compute_window_length_sum(s) << NEWLINE;
	}

	auto output_string = output.str();

	std::string output_filename = args.get_arg_value("--output");
	if (!output_filename.empty())
	{
		std::ofstream output_file(output_filename, std::fstream::app);

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
