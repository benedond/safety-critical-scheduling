#include <iostream>
#include <unordered_set>
#include <vector>
#include <cassert>
#include <cmath>

#include "simple_solver.h"

simple_solver::simple_solver(const Environment &e, const std::unordered_map<std::string, Task> &t)
		: m_environment(e), m_tasks(t), m_solved(false), m_feasible(false)
{
}

Solution simple_solver::get_solution()
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

	std::vector<const Task*> tasks;
	std::unordered_set<const Task*> assigned_tasks(m_tasks.size());

	tasks.reserve(m_tasks.size());
	for (auto& task : m_tasks)
		tasks.push_back(&task.second);

	std::sort(tasks.begin(), tasks.end(), [](const Task* a, const Task* b) {
		return a->length > b->length;
	});

	auto task_count = m_tasks.size();
	Window window { .length = -1 };

	std::unordered_map<std::string, int> proc_unit_allocation;

	while (assigned_tasks.size() < task_count)
	{
		for (auto& task : tasks)
		{
			if (assigned_tasks.find(task) != assigned_tasks.end())
				continue;

			// can task be assigned to all required processors?
			for (auto& p : task->processors)
				if (proc_unit_allocation[p] >= m_environment.processors.at(p).processing_units)
					goto task_assignment_loop; // can't assign task to current window, try to find another one

			// task can be assigned: assign it to all required processors
			{
				for (auto& p : task->processors)
					proc_unit_allocation[p] = proc_unit_allocation[p] + 1;

				// check window length
				float wl = ceilf((float) task->length / 0.6f);
				if ((float) window.length < wl)
					window.length = (int) wl;

				// assign task to current window
				window.tasks.push_back(task->name);
				assigned_tasks.insert(task);

				//goto solver_loop; // continue with task assignment
				//task_assigned = true;
				//break;
			}

			task_assignment_loop:;
		}

		//if (window.length == -1)
		//{
		//	std::cerr << "ERROR";
		//	break;
		//}
		assert(window.length > 0);

		window = save_window(std::move(window));
		if (!check_feasibility())
			return;

		proc_unit_allocation.clear();
		solver_loop:;
	}

	m_feasible = true;
}

Window simple_solver::save_window(Window&& window)
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