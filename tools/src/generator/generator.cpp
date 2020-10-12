#include <iostream>
#include <chrono>
#include <exception>

#include "generator.h"

generator::generator(const arg_parser& args, const environment& e) : m_environment(e)
{
	args.set_arg_value_int("--min-length", &this->m_min_length);
	args.set_arg_value_int("--max-length", &this->m_max_length);
	args.set_arg_value_int("--coprocessor-probability", &this->m_coprocessor_probability);
	args.set_arg_value_int("--task-count", &this->m_task_count);

	if (std::find(m_supported_problem_versions.begin(),
				  m_supported_problem_versions.end(),
				  m_environment.problem_version) == m_supported_problem_versions.end())
		throw std::invalid_argument("problem version is not supported");

	if (m_min_length > m_max_length)
		throw std::invalid_argument("min task length is greater than max task length");
}

std::vector<task> generator::generate() const
{
	std::vector<task> tasks;

	std::vector<std::string> main_processors;
	std::vector<std::string> coprocessors;

	for (auto& processor : m_environment.processors)
	{
		if (processor.second.type == processor_type::main_processor)
			main_processors.push_back(processor.second.name);
		else if (processor.second.type == processor_type::coprocessor)
			coprocessors.push_back(processor.second.name);
	}

	if (coprocessors.empty() && m_coprocessor_probability > 0)
		std::cerr << "coprocessor probability is > 0, but no coprocessors were found in the environment" << std::endl;

	std::mt19937 random_engine(std::chrono::high_resolution_clock::now().time_since_epoch().count());

	std::uniform_int_distribution<int> task_length_dist(m_min_length, m_max_length);
	std::uniform_int_distribution<int> processor_dist(0, main_processors.size()-1);
	std::uniform_int_distribution<int> use_coprocessor_dist(1, 100);
	std::uniform_int_distribution<int> coprocessor_dist(0, coprocessors.size()-1);

	for (int i=0; i<m_task_count; i++)
	{
		task t;

		t.name = "T" + std::to_string(i);
		t.length = task_length_dist(random_engine);

		int processor_ix = processor_dist(random_engine);
		t.processors.push_back({ .processor = main_processors[processor_ix], .processing_units = 1 });

		int use_coprocessor = use_coprocessor_dist(random_engine);
		if (use_coprocessor < m_coprocessor_probability)
		{
			int coprocessor_ix = coprocessor_dist(random_engine);
			t.processors.push_back({ .processor = coprocessors[coprocessor_ix], .processing_units = 1 });
		}

		tasks.push_back(std::move(t));
	}

	return tasks;
}