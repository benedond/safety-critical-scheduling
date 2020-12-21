#include <iostream>
#include <chrono>
#include <exception>
#include <fstream>
#include <unordered_set>
#include <cmath>

#include "p1_generator.h"

const static std::string benchmark_keyword = "benchmark";
const static std::string utf8_benchmark_keyword = "\uFEFFbenchmark";
const static std::string slope_keyword = "slope";
const static std::string intercept_keyword = "intercept";
const static std::string csv_header_expression_separator = "_";
const static auto slope_substr_length = csv_header_expression_separator.length() + slope_keyword.length();
const static auto intercept_substr_length = csv_header_expression_separator.length() + intercept_keyword.length();

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
		                   const std::vector<std::vector<std::string>>& apc,
						   const std::unordered_map<std::string, std::unordered_map<std::string, benchmark_entry>>& be)
	: m_environment(e), m_active_processor_combinations(apc), m_benchmark_entries(be)
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

	m_adjust_weights_by_proc_time = args.is_arg_present("--adjust-weights");
}

std::vector<assignment_characteristic> p1_generator::generate() const
{
	std::vector<assignment_characteristic> tasks;
	tasks.reserve(m_task_count);

	std::vector<std::string> benchmarks;
	benchmarks.reserve(m_benchmark_entries.size());

	for (auto& be : m_benchmark_entries)
		benchmarks.push_back(be.first);

	std::mt19937 random_engine(std::chrono::high_resolution_clock::now().time_since_epoch().count());

	std::uniform_int_distribution<int> task_length_dist(m_min_length, m_max_length);
	std::uniform_int_distribution<int> benchmark_dist(0, benchmarks.size()-1);

	for (int i=0; i<m_task_count; i++)
	{
		assignment_characteristic task;

		int base_length = task_length_dist(random_engine);
		int num_iterations = -1;
		int benchmark_ix = benchmark_dist(random_engine);

		auto& benchmark_name = benchmarks[benchmark_ix];
		task.task = std::to_string(i) + "_" + benchmark_name;
		task.command = benchmark_name;

		for (auto& pc : m_active_processor_combinations)
		{
			std::string pc_string = create_processor_combination_expression(pc);
			auto& be = m_benchmark_entries.at(benchmark_name).at(pc_string);

			if (num_iterations < 0)
				num_iterations = (int) std::ceil((float) base_length / be.proc_time);
			int length = (int) std::ceil((float) num_iterations * be.proc_time);
			int weight_adjust_factor = m_adjust_weights_by_proc_time ? length : 1;

			assignment_characteristic::resource_assignment ra { .energy_consumption = be.weight * weight_adjust_factor,
													            .length = length };
			for (auto& p : pc)
				ra.processors.push_back({ .processor = p, .processing_units = 1 });
			task.resource_assignments.push_back(std::move(ra));
		}

		tasks.push_back(std::move(task));
	}

	return tasks;
}

//old parser for the more complicated format
//std::pair<std::vector<std::vector<std::string>>, std::unordered_map<std::string, std::unordered_map<std::string, benchmark_entry>>> parse_benchmark_data(
//		const std::unordered_map<std::string, processor>& processors,
//		std::ifstream& benchmark_data_file,
//		const std::string& csv_separator)
//{
//	std::vector<std::vector<std::string>> active_processor_combinations;
//	std::unordered_map<std::string, std::unordered_map<std::string, benchmark_entry>> benchmark_entries;
//
//	std::string header;
//	std::getline(benchmark_data_file, header);
//
//	int benchmark_column_index = -1;
//	std::unordered_map<std::string, int> slopes, intercepts;
//
//	auto columns = split_string(header, csv_separator);
//	for (int i=0; i<columns.size(); i++)
//	{
//		auto& column = columns[i];
//		auto column_parts = split_string(column, csv_header_expression_separator);
//		auto column_parts_size = column_parts.size();
//
//		if (column_parts[column_parts_size-1] == benchmark_keyword || column_parts[column_parts_size-1] == utf8_benchmark_keyword)
//		{
//			benchmark_column_index = i;
//		}
//		else if (column_parts[column_parts_size-1] == slope_keyword)
//		{
//			std::string processor_combo_string = column.substr(0, column.length() - slope_substr_length);
//			slopes[processor_combo_string] = i;
//		}
//		else if (column_parts[column_parts_size-1] == intercept_keyword)
//		{
//			std::string processor_combo_string = column.substr(0, column.length() - intercept_substr_length);
//			intercepts[processor_combo_string] = i;
//		}
//		else
//		{
//          // todo a_p_c.push_back(column_parts) ?
//			std::vector<std::string> processor_combination;
//			for (auto& p : column_parts)
//				processor_combination.push_back(p);
//			active_processor_combinations.push_back(std::move(processor_combination));
//		}
//	}
//
//	int columns_required = 3*active_processor_combinations.size() + 1;
//
//	while (true)
//	{
//		std::string line;
//		std::getline(benchmark_data_file, line);
//		if (line.empty())
//			break;
//
//		auto line_parts = split_string(std::move(line), csv_separator);
//		if (line_parts.size() < columns_required)
//			break;
//
//		auto& be = benchmark_entries[line_parts[benchmark_column_index]];
//		for (auto& combo : active_processor_combinations)
//		{
//			std::string combo_string = create_processor_combination_expression(combo);
//
//			auto& data = be[combo_string];
//			data.slope = std::stof(line_parts[slopes.at(combo_string)]);
//			data.intercept = std::stof(line_parts[intercepts.at(combo_string)]);
//		}
//	}
//
//	return std::make_pair(active_processor_combinations, benchmark_entries);
//}

std::pair<std::vector<std::vector<std::string>>, std::unordered_map<std::string, std::unordered_map<std::string, benchmark_entry>>> parse_benchmark_data(
		const std::unordered_map<std::string, processor>& processors,
		std::ifstream& benchmark_data_file,
		const std::string& csv_separator)
{
	std::vector<std::vector<std::string>> active_processor_combinations;
	std::unordered_map<std::string, std::unordered_map<std::string, benchmark_entry>> benchmark_entries;
	std::unordered_set<std::string> combo_strings;

	std::string header;
	std::getline(benchmark_data_file, header);

	while (true)
	{
		std::string line;
		std::getline(benchmark_data_file, line);
		if (line.empty())
			break;

		auto line_parts = split_string(std::move(line), csv_separator);
		if (line_parts.size() < 7)
			break;

		auto& combo_string = line_parts[0];
		combo_strings.insert(combo_string);

		auto& be = benchmark_entries[line_parts[1]];
		auto& benchmark_data = be[combo_string];

		benchmark_data.slope = std::stof(line_parts[3]);
		benchmark_data.intercept = std::stof(line_parts[2]);
		benchmark_data.proc_time = std::stof(line_parts[4]);
		benchmark_data.weight = std::stof(line_parts[6]);
		benchmark_data.proc_units = std::stoi(line_parts[5]);
	}

	active_processor_combinations.reserve(combo_strings.size());
	for (auto& cs : combo_strings)
		active_processor_combinations.push_back(split_string(cs, csv_header_expression_separator));

	return std::make_pair(active_processor_combinations, benchmark_entries);
}