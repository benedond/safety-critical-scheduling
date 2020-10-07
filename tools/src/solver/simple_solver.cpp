#include <iostream>
#include <vector>
#include <cassert>
#include <cmath>
#include <set>

#include "simple_solver.h"

simple_solver::simple_solver(const environment& e, const task_map& t)
		: m_environment(e), m_tasks(t), m_solved(false), m_feasible(false)
{
}

solution simple_solver::get_solution()
{
	if (!m_solved)
		solve();

	if (m_feasible)
		return { .feasible = true, .windows = m_windows };
	else
		return { .feasible = false };
}

void simple_solver::solve()
{
	if (m_solved)
		return;
	m_solved = true;

	const static auto task_comparator = [](const task* a, const task* b) { return a->length != b->length ? a->length > b->length : a > b; };
	std::set<const task*, decltype(task_comparator)> unassigned_tasks(task_comparator);

	for (auto& task : m_tasks)
		unassigned_tasks.insert(&task.second);

	window window { .length = -1 };
	std::unordered_map<std::string, int> proc_unit_allocation;

	while (!unassigned_tasks.empty())
	{
		for (auto& task : unassigned_tasks)
		{
			// can task be assigned to all required processors?
			for (auto& p : task->processors)
			{
				int required_processing_units = p.processing_units;
				int available_processing_units = m_environment.processors.at(p.processor).processing_units - proc_unit_allocation[p.processor];

				if (available_processing_units < required_processing_units)
					goto task_assignment_loop; // can't assign task to current window, try to find another one
			}

			// task can be assigned: assign it to all required processors by generating appropriate task assignments
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

				unassigned_tasks.erase(task);
			}

			task_assignment_loop:;
		}

		assert(window.length > 0);

		window = save_window(std::move(window));
		if (!check_feasibility())
			return;

		proc_unit_allocation.clear();
	}

	m_feasible = true;
}

window simple_solver::save_window(window&& window)
{
	m_windows.push_back(std::move(window));
	return { .length = -1 };
}

bool simple_solver::check_feasibility()
{
	int total_time = 0;
	for (auto& w : m_windows)
		total_time += w.length;

	if (total_time > m_environment.main_frame_length)
	{
		std::cerr << "solution is infeasible - total_time: " << total_time << " main_frame_length: " << m_environment.main_frame_length << std::endl;
		return false;
	}

	return true;
}