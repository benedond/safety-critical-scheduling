#ifndef INSTANCE_GENERATOR_H
#define INSTANCE_GENERATOR_H

#include <random>
#include <unordered_set>

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

class instance_generator
{
public:
	std::vector<assignment_characteristic> generate() const;

	instance_generator(const arg_parser& args, const environment& e, const benchmark_data& bd);

private:
	const std::unordered_set<int> m_supported_problem_versions{ 1, 2 };

	const environment& m_environment;
	const benchmark_data& m_benchmark_data;

	int m_min_length = 40, m_max_length = 160;
	int m_task_count = 20;
	int seed_val = 0;
};

benchmark_data parse_benchmark_data(
		const std::unordered_map<std::string, processor>& processors,
		std::ifstream& benchmark_data_file,
		const std::string& csv_separator = ",");

int calculate_major_frame_length(const environment& env, const std::vector<assignment_characteristic>& assignment_characteristics);

#endif // INSTANCE_GENERATOR_H
