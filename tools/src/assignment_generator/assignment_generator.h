#ifndef ASSIGNMENT_GENERATOR_H
#define ASSIGNMENT_GENERATOR_H

#include <random>
#include <array>

#include "../common/instance.h"
#include "../common/arg_parser.h"

class assignment_generator
{
public:
	std::vector<task> generate() const;

	assignment_generator(const arg_parser& args, const environment& e);

private:
	const std::array<int, 2> m_supported_problem_versions{ 1, 2 };

	const environment& m_environment;

	int m_min_length = 1, m_max_length = 40;
	int m_coprocessor_probability = 30;
	int m_task_count = 12;
};

#endif // ASSIGNMENT_GENERATOR_H
