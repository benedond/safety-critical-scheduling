#include <iostream>
#include <vector>
#include <cassert>
#include <cmath>
#include <random>
#include <chrono>

#include "random_task_order_solver.h"

random_task_order_solver::random_task_order_solver(const environment& e, const task_map& t)
		: solver(e, t), m_seed(std::chrono::high_resolution_clock::now().time_since_epoch().count())
{
}

void random_task_order_solver::solve()
{
	if (m_solved)
		return;
	m_solved = true;

	/*const static auto task_comparator = [](const task* a, const task* b) { return a->length != b->length ? a->length > b->length : a > b; };
	std::set<const task*, decltype(task_comparator)> unassigned_tasks(task_comparator);*/
	std::vector<const task*> unassigned_tasks;

	for (auto& task : m_tasks)
		unassigned_tasks.push_back(&task.second);

	std::mt19937 random_generator(m_seed);
	std::shuffle(unassigned_tasks.begin(), unassigned_tasks.end(), random_generator);

	window window { .length = -1 };
	std::unordered_map<std::string, int> proc_unit_allocation;

	while (!unassigned_tasks.empty())
	{
		for (auto itt = unassigned_tasks.begin(); itt != unassigned_tasks.end(); )
		{
			auto task = *itt;
			bool can_assign_task = true;

			// can task be assigned to all required processors?
			for (auto& p : task->processors)
			{
				int required_processing_units = p.processing_units;
				int available_processing_units = m_environment.processors.at(p.processor).processing_units - proc_unit_allocation[p.processor];

				if (available_processing_units < required_processing_units)
				{
					// can't assign task to current window, try to find another one
					//goto task_assignment_loop;
					can_assign_task = false;
					itt++;
					break;
				}
			}

			// task can be assigned: assign it to all required processors by generating appropriate task assignments
			if (can_assign_task)
			{
				std::vector<window::task_assignment> task_assignments;
				for (auto& p : task->processors)
				{
					int start_proc_unit = proc_unit_allocation[p.processor];
					for (int i=0; i<p.processing_units; i++)
					{
						task_assignments.push_back({ .task = task->name,
														   .processor = p.processor,
														   .processing_unit = start_proc_unit+i,
														   .start = 0,
														   .length = task->length });
					}
					proc_unit_allocation[p.processor] = start_proc_unit + p.processing_units;
				}

				// check window length
				float wl = ceilf((float) task->length / 0.6f);
				if ((float) window.length < wl)
					window.length = (int) wl;

				// assign task to current window
				for (auto& task_assignment : task_assignments)
					window.task_assignments.push_back(std::move(task_assignment));

				itt = unassigned_tasks.erase(itt);
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

bool random_task_order_solver::check_problem_compatibility() const
{
	return std::find(m_supported_problem_versions.begin(),
					 m_supported_problem_versions.end(),
					 m_environment.problem_version) != m_supported_problem_versions.end();
}

std::string random_task_order_solver::get_solver_name() const
{
	return "random task order solver";
}

solver::metadata_map random_task_order_solver::get_solver_metadata() const
{
	return metadata_map {
			{"seed", std::to_string(m_seed)}
	};
}