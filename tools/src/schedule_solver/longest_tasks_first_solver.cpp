#include <iostream>
#include <vector>
#include <unordered_set>
#include <cassert>
#include <cmath>
#include <set>

#include "longest_tasks_first_solver.h"

longest_tasks_first_solver::longest_tasks_first_solver(const environment& e, const task_map& t)
	: solver(e, t), m_out_of_order_task_count(0)
{
}

void longest_tasks_first_solver::solve()
{
	if (m_solved)
		return;
	m_solved = true;

	const static auto task_comparator = [](const task* a, const task* b) { return a->length != b->length ? a->length > b->length : a > b; };
	std::set<const task*, decltype(task_comparator)> unassigned_tasks(task_comparator);

	for (auto& task : m_tasks)
		unassigned_tasks.insert(&task.second);

	int primary_processor_count = 0;
	for (auto& p : m_environment.processors)
		if (p.second.type == processor_type::main_processor)
			primary_processor_count++;

	window window { .length = -1 };
	std::unordered_map<std::string, int> proc_unit_allocation;

	while (!unassigned_tasks.empty())
	{
		int full_primary_processors_count = 0;

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
					m_out_of_order_task_count++;
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

					auto& processor_data = m_environment.processors.at(p.processor);
					if (processor_data.type == processor_type::main_processor &&
						proc_unit_allocation[p.processor] >= processor_data.processing_units)
					{
						full_primary_processors_count++;
					}
				}

				// check window length
				float wl = ceilf((float) task->length / m_environment.sc_part);
				if ((float) window.length < wl)
					window.length = (int) wl;

				// assign task to current window
				for (auto& task_assignment : task_assignments)
					window.task_assignments.push_back(std::move(task_assignment));

				itt = unassigned_tasks.erase(itt);
			}

			if (full_primary_processors_count >= primary_processor_count)
				break;
		}

		assert(window.length > 0);

		window = save_window(std::move(window));
		if (!check_feasibility())
			return;

		proc_unit_allocation.clear();
	}

	m_feasible = true;
}

bool longest_tasks_first_solver::check_problem_compatibility() const
{
	return m_supported_problem_versions.find(m_environment.problem_version) != m_supported_problem_versions.end();
}

std::string longest_tasks_first_solver::get_solver_name() const
{
	return "longest tasks first solver";
}

solver::metadata_map longest_tasks_first_solver::get_solver_metadata() const
{
	return metadata_map {
		{"outOfOrderTaskCount", std::to_string(m_out_of_order_task_count)}
	};
}