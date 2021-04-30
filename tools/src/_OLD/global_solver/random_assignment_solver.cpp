#include <iostream>
#include <vector>
#include <random>
#include <chrono>

#include "random_assignment_solver.h"

random_assignment_solver::random_assignment_solver(const environment& e, const assignment_characteristic_list& t)
		: global_solver(e, t), m_seed(std::chrono::high_resolution_clock::now().time_since_epoch().count())
{
}

void random_assignment_solver::solve()
{
	if (m_solved)
		return;
	m_solved = true;

	std::vector<const assignment_characteristic*> tasks;
	tasks.reserve(m_assignments.size());
	for (auto& task : m_assignments)
		tasks.push_back(&task);

	std::mt19937 random_generator(m_seed);
	std::shuffle(tasks.begin(), tasks.end(), random_generator);

	std::uniform_int_distribution<> assignment_dist(0, 99);

	while (!tasks.empty())
	{
		auto task = tasks.back();
		tasks.pop_back();

		int sel_assignment = assignment_dist(random_generator) % (int) task->resource_assignments.size();
		auto& assignment = task->resource_assignments[sel_assignment];

		m_tasks.push_back({ .name = task->task,
			 .command = task->command,
			 .length = assignment.length,
			 .assignment_index = sel_assignment,
			 .processors = assignment.processors });

	}

	m_feasible = true;
}

bool random_assignment_solver::check_problem_compatibility() const
{
	return std::find(m_supported_problem_versions.begin(),
					 m_supported_problem_versions.end(),
					 m_environment.problem_version) != m_supported_problem_versions.end();
}

std::string random_assignment_solver::get_solver_name() const
{
	return "random assignment solver";
}

global_solver::metadata_map random_assignment_solver::get_solver_metadata() const
{
	return metadata_map {
			{"seed", std::to_string(m_seed)}
	};
}