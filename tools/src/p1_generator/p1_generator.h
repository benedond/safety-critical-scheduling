#ifndef P1_GENERATOR_H
#define P1_GENERATOR_H

#include <random>
#include <array>

#include "../common/instance.h"
#include "../common/arg_parser.h"

struct benchmark_entry
{
	float slope, intercept, proc_time, weight;
	int proc_units;
};

class p1_generator
{
public:
	std::vector<assignment_characteristic> generate() const;

	p1_generator(const arg_parser& args, const environment& e,
				 const std::vector<std::vector<std::string>>& apc,
			     const std::unordered_map<std::string, std::unordered_map<std::string, benchmark_entry>>& be);

private:
	const std::array<int, 1> m_supported_problem_versions{ 1 };

	const environment& m_environment;
	const std::unordered_map<std::string, std::unordered_map<std::string, benchmark_entry>>& m_benchmark_entries;
	const std::vector<std::vector<std::string>>& m_active_processor_combinations;

	int m_min_length = 10, m_max_length = 50;
	int m_task_count = 10;
};

std::pair<std::vector<std::vector<std::string>>, std::unordered_map<std::string, std::unordered_map<std::string, benchmark_entry>>> parse_benchmark_data(
		const std::unordered_map<std::string, processor>& processors,
		std::ifstream& benchmark_data_file,
		const std::string& csv_separator = ",");

#endif // P1_GENERATOR_H
