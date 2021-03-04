#include <iostream>
#include <chrono>
#include <exception>
#include <unordered_set>
#include <cmath>
#include <fstream>

#include "p1_generator.h"

const static std::string affinity_keyword = "affinity";
const static std::string benchmark_keyword = "benchmark";
//const static std::string utf8_benchmark_keyword = "\uFEFFbenchmark";
const static std::string slope_keyword = "slope";
const static std::string intercept_keyword = "intercept";
const static std::string runtime_keyword = "runtime";
const static std::string command_keyword = "intercept";
const static std::string csv_header_expression_separator = "_";


static inline std::string create_processor_combination_expression(const std::vector<std::string>& processors)
{
	std::string combo_string;
	int combo_size = processors.size();

	for (int i=0; i<combo_size; i++)
	{
		combo_string += processors[i];
		if (i < combo_size - 1)
			combo_string += csv_header_expression_separator;
	}

	return combo_string;
}

static inline std::vector<std::string> split_string(std::string s, const std::string& delimiter)
{
	auto delimiter_length = delimiter.length();
	std::vector<std::string> items;

	size_t pos;
	while ((pos = s.find(delimiter)) != std::string::npos)
	{
		items.push_back(s.substr(0, pos));
		s.erase(0, pos+delimiter_length);
	}

	if (!s.empty())
		items.push_back(std::move(s));

	return items;
}

p1_generator::p1_generator(const arg_parser& args,
		                   const environment& e,
		                   const benchmark_data& be)
	: m_environment(e), m_benchmark_data(be)
{
	args.set_arg_value_int("--min-length", &this->m_min_length);
	args.set_arg_value_int("--max-length", &this->m_max_length);
	args.set_arg_value_int("--task-count", &this->m_task_count);

	if (std::find(m_supported_problem_versions.begin(),
				  m_supported_problem_versions.end(),
				  m_environment.problem_version) == m_supported_problem_versions.end())
		throw std::invalid_argument("problem version is not supported");

	if (m_min_length > m_max_length)
		throw std::invalid_argument("min task length is greater than max task length");
}

std::vector<assignment_characteristic> p1_generator::generate() const
{
	std::vector<assignment_characteristic> tasks;
	tasks.reserve(m_task_count);

	std::vector<std::string> benchmarks;
	benchmarks.reserve(m_benchmark_data.benchmark_entries.size());

	for (auto& be : m_benchmark_data.benchmark_entries)
		benchmarks.push_back(be.first);

	std::mt19937 random_engine(std::chrono::high_resolution_clock::now().time_since_epoch().count());

	std::uniform_int_distribution<int> task_length_dist(m_min_length, m_max_length);
	std::uniform_int_distribution<int> benchmark_dist(0, benchmarks.size()-1);

	for (int i=0; i<m_task_count; i++)
	{
		assignment_characteristic task;

		int base_length = task_length_dist(random_engine);
		float num_iterations = -1;
		int benchmark_ix = benchmark_dist(random_engine);

		auto& benchmark_name = benchmarks[benchmark_ix];
		task.task = std::to_string(i) + "_" + benchmark_name;
		task.command = benchmark_name;

		for (auto& pc : m_benchmark_data.active_processor_combinations)
		{
			std::string pc_string = create_processor_combination_expression(pc);
			auto& be = m_benchmark_data.benchmark_entries.at(benchmark_name).at(pc_string);

			if (num_iterations < 0)
			{
				num_iterations = (float) base_length / be.proc_time;
				if (m_benchmark_data.benchmark_commands.find(benchmark_name) != m_benchmark_data.benchmark_commands.end())
				{
					auto& bcmd = m_benchmark_data.benchmark_commands.at(benchmark_name);
					if (bcmd.find(pc_string) != bcmd.end())
						task.command = bcmd.at(pc_string);
				}
			}
			int length = (int) std::ceil((float) num_iterations * be.proc_time);

			assignment_characteristic::resource_assignment ra { .slope = be.slope,
													   			.intercept = be.intercept,
													            .length = length };
			for (auto& p : pc)
				ra.processors.push_back({ .processor = p, .processing_units = 1 });
			task.resource_assignments.push_back(std::move(ra));
		}

		tasks.push_back(std::move(task));
	}

	return tasks;
}

benchmark_data parse_benchmark_data(
		const std::unordered_map<std::string, processor>& processors,
		std::ifstream& benchmark_data_file,
		const std::string& csv_separator)
{
	int benchmark_column_index = 0,
		affinity_column_index = 1,
		slope_column_index = 2,
		intercept_column_index = 3,
		runtime_column_index = 4,
		command_column_index = -1;

	std::vector<std::vector<std::string>> active_processor_combinations;
	std::unordered_map<std::string, std::unordered_map<std::string, benchmark_entry>> benchmark_entries;
	std::unordered_map<std::string, std::unordered_map<std::string, std::string>> benchmark_commands;
	std::unordered_set<std::string> combo_strings;

	std::string header;
	std::getline(benchmark_data_file, header);
	auto header_parts = split_string(std::move(header), csv_separator);

	int ix = 0;
	for (auto& hp : header_parts)
	{
		if (hp == benchmark_keyword) benchmark_column_index = ix;
		else if (hp == affinity_keyword) affinity_column_index = ix;
		else if (hp == slope_keyword) slope_column_index = ix;
		else if (hp == intercept_keyword) intercept_column_index = ix;
		else if (hp == runtime_keyword) runtime_column_index = ix;
		else if (hp == command_keyword) command_column_index = ix;
		ix++;
	}

	while (true)
	{
		std::string line;
		std::getline(benchmark_data_file, line);
		if (line.empty())
			break;

		try
		{
			auto line_parts = split_string(std::move(line), csv_separator);

			auto& combo_string = line_parts[affinity_column_index];
			combo_strings.insert(combo_string);

			auto& benchmark = line_parts[benchmark_column_index];
			auto& benchmark_data = benchmark_entries[benchmark][combo_string];

			benchmark_data.slope = std::stof(line_parts[slope_column_index]);
			benchmark_data.intercept = std::stof(line_parts[intercept_column_index]);
			benchmark_data.proc_time = std::stof(line_parts[runtime_column_index]);
			if (command_column_index != -1)
				auto& bc = benchmark_commands[benchmark][combo_string] = line_parts[command_column_index];
		}
		catch (std::exception& e)
		{
			std::cerr << "error parsing benchmark data";
			exit(1);
		}
	}

	active_processor_combinations.reserve(combo_strings.size());
	for (auto& cs : combo_strings)
		active_processor_combinations.push_back(split_string(cs, csv_header_expression_separator));

	return { .active_processor_combinations = std::move(active_processor_combinations),
		  	 .benchmark_entries = std::move(benchmark_entries),
		  	 .benchmark_commands = std::move(benchmark_commands) };
}