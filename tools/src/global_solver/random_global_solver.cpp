#include <iostream>
#include <vector>
#include <cassert>
#include <cmath>
#include <random>
#include <chrono>

#include "random_global_solver.h"

random_global_solver::random_global_solver(const environment& e, const assignment_characteristic_list& t)
		: global_solver(e, t), m_seed(std::chrono::high_resolution_clock::now().time_since_epoch().count())
{
}

void random_global_solver::solve()
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

	window window { .length = -1 };
	std::unordered_map<std::string, int> proc_unit_allocation;

	int total_capacity = 0;
	for (auto& p : m_environment.processors)
		if (p.second.type == processor_type::main_processor)
			total_capacity += p.second.processing_units;

	std::uniform_int_distribution<> num_assigned_tasks_dist(total_capacity*5/6, total_capacity);
	std::uniform_int_distribution<> assignment_dist(0, 99);

	while (!tasks.empty())
	{
		int num_assigned_tasks = std::min(num_assigned_tasks_dist(random_generator), (int) tasks.size());

		for (int i=0; i<num_assigned_tasks; i++)
		{
			auto task = tasks.back();
			tasks.pop_back();

			int sel_assignment = assignment_dist(random_generator) % (int) task->resource_assignments.size();
			int iterations = 0;
			for (;; sel_assignment = (sel_assignment+1) % (int) task->resource_assignments.size())
			{
				auto& assignment = task->resource_assignments[sel_assignment];

				if (iterations++ > task->resource_assignments.size())
				{
					std::cerr << "fatal error: task assignment unexpectedly failed" << std::endl;
					return;
				}
				bool can_assign_task = true;

				// can task be assigned to all required processors?
				for (auto& p : assignment.processors)
				{
					int required_processing_units = p.processing_units;
					int available_processing_units = m_environment.processors.at(p.processor).processing_units - proc_unit_allocation[p.processor];

					if (available_processing_units < required_processing_units)
					{
						// can't assign task to current window
						can_assign_task = false;
						break;
					}
				}

				// task can be assigned: assign it to all required processors by generating appropriate task assignments
				if (can_assign_task)
				{
					std::vector<window::task_assignment> task_assignments;
					for (auto& p : assignment.processors)
					{
						int start_proc_unit = proc_unit_allocation[p.processor];
						for (int j = 0; j < p.processing_units; j++)
						{
							task_assignments.push_back({.task = task->task,
															   .processor = p.processor,
															   .processing_unit = start_proc_unit + j,
															   .start = 0,
															   .length = assignment.length});
						}
						proc_unit_allocation[p.processor] = start_proc_unit + p.processing_units;
					}

					// check window length
					float wl = ceilf((float) assignment.length / m_environment.sc_part);
					if ((float) window.length < wl)
						window.length = (int) wl;

					// assign task to current window
					for (auto& task_assignment : task_assignments)
						window.task_assignments.push_back(std::move(task_assignment));

					m_tasks.push_back({ .name = task->task,
						 .command = task->command,
						 .length = assignment.length,
						 .assignment_index = sel_assignment,
						 .processors = assignment.processors });

					break;
				}
			}
		}

		assert(window.length > 0);

		window = save_window(std::move(window));
		if (!check_feasibility())
			return;

		proc_unit_allocation.clear();
	}

	m_feasible = true;
}

bool random_global_solver::check_problem_compatibility() const
{
	return std::find(m_supported_problem_versions.begin(),
					 m_supported_problem_versions.end(),
					 m_environment.problem_version) != m_supported_problem_versions.end();
}

std::string random_global_solver::get_solver_name() const
{
	return "random global solver";
}

global_solver::metadata_map random_global_solver::get_solver_metadata() const
{
	return metadata_map {
			{"seed", std::to_string(m_seed)}
	};
}