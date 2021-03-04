#ifndef P1_GENERATOR_H
#define P1_GENERATOR_H

#include <random>
#include <array>

#include "../common/instance.h"
#include "../common/arg_parser.h"

struct benchmark_entry
{
	float slope, intercept, proc_time;
};

struct benchmark_data
{
	std::vector<std::vector<std::string>> active_processor_combinations;
	std::unordered_map<std::string, std::unordered_map<std::string, benchmark_entry>> benchmark_entries;
	std::unordered_map<std::string, std::unordered_map<std::string, std::string>> benchmark_commands;
};

class p1_generator
{
public:
	std::vector<assignment_characteristic> generate() const;

	p1_generator(const arg_parser& args, const environment& e, const benchmark_data& bd);

private:
	const std::array<int, 2> m_supported_problem_versions{ 1, 2 };

	const environment& m_environment;
	const benchmark_data& m_benchmark_data;

	int m_min_length = 50, m_max_length = 150;
	int m_task_count = 15;
};

benchmark_data parse_benchmark_data(
		const std::unordered_map<std::string, processor>& processors,
		std::ifstream& benchmark_data_file,
		const std::string& csv_separator = ",");

#endif // P1_GENERATOR_H
