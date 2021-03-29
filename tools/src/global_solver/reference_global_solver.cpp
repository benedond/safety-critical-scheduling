#include <iostream>
#include <vector>
#include <unordered_set>
#include <set>


#include "reference_global_solver.h"

struct simple_task_assignment
{
	std::string task, command;
	float slope, intercept;
	int length, assignment_index;
	std::vector<task::processor_assignment> processors;

	float sort_value() const
	{
		return (float) length * slope;
	}

	bool operator<(const simple_task_assignment& other) const
	{
		return sort_value() < other.sort_value();
	}

	bool operator>(const simple_task_assignment& other) const
	{
		return sort_value() > other.sort_value();
	}
};

reference_global_solver::reference_global_solver(const environment& e, const assignment_characteristic_list& t)
		: global_solver(e, t)
{
}

void reference_global_solver::solve()
{
	if (m_solved)
		return;
	m_solved = true;

	std::set<simple_task_assignment, std::less<>> tasks_to_schedule;
	std::unordered_set<std::string> scheduled_tasks;
	const int num_of_tasks_to_schedule = m_assignments.size();

	for (auto& ac : m_assignments)
	{
		int i=0;
		for (auto& ra : ac.resource_assignments)
		{
			tasks_to_schedule.insert({.task = ac.task,
											 .command = ac.command,
											 .slope = ra.slope,
											 .intercept = ra.intercept,
											 .length = ra.length,
											 .assignment_index = i++,
											 .processors = ra.processors});
		}
	}

	std::unordered_map<int, std::unordered_map<std::string, int>> pu_allocations;
	m_tasks.reserve(num_of_tasks_to_schedule);
	m_windows.push_back({});
	for (const auto& assignment : tasks_to_schedule)
	{
		if (scheduled_tasks.find(assignment.task) != scheduled_tasks.end())
			continue;

		// try to find an available window
		int target_window = -1;
		for (int w=0; w<m_windows.size(); w++)
		{
			bool can_assign_task = true;
			// can task be assigned to all required processors?
			for (auto& p : assignment.processors)
			{
				int required_processing_units = p.processing_units;
				int available_processing_units =
						m_environment.processors.at(p.processor).processing_units - pu_allocations[w][p.processor];

				if (available_processing_units < required_processing_units)
				{
					// window does not have all the required resources available
					can_assign_task = false;
					break;
				}
			}

			if (can_assign_task)
			{
				if (target_window == -1 ||
					(m_windows[target_window].length - assignment.length < 0 && m_windows[w].length - assignment.length >= 0) ||
					(std::abs(m_windows[w].length - assignment.length) < std::abs(m_windows[target_window].length - assignment.length)) &&
						((m_windows[target_window].length - assignment.length < 0 && m_windows[w].length - assignment.length < 0) ||
					 	(m_windows[target_window].length - assignment.length >= 0 && m_windows[w].length - assignment.length >= 0))
					)
					target_window = w;
			}
		}

		// no available window found
		if (target_window == -1)
		{
			m_windows.push_back({});
			target_window = (int) m_windows.size() - 1;
		}

		// check window length
		auto& window = m_windows[target_window];
		float wl = ceilf((float) assignment.length / m_environment.sc_part);
		if ((float) window.length < wl)
		{
			int old_window_length = window.length;
			window.length = (int) wl;
			// check mf constraint

			if (!check_feasibility())
			{
				// REJECT ASSIGNMENT
				window.length = old_window_length;
				continue;
			}
		}

		// ACCEPT ASSIGNMENT
		std::vector<window::task_assignment> task_assignments;
		for (auto& p : assignment.processors)
		{
			int start_proc_unit = pu_allocations[target_window][p.processor];
			for (int j = 0; j < p.processing_units; j++)
			{
				task_assignments.push_back({.task = assignment.task,
												   .processor = p.processor,
												   .processing_unit = start_proc_unit + j,
												   .start = 0,
												   .length = assignment.length});
			}
			pu_allocations[target_window][p.processor] = start_proc_unit + p.processing_units;
		}

		for (auto& task_assignment : task_assignments)
			window.task_assignments.push_back(std::move(task_assignment));

		m_tasks.push_back({.name = assignment.task,
								.command = assignment.command,
								.length = assignment.length,
								.assignment_index = assignment.assignment_index,
								.processors = assignment.processors});


		scheduled_tasks.insert(assignment.task);

	}

	assert(scheduled_tasks.size() <= num_of_tasks_to_schedule);
	m_feasible = num_of_tasks_to_schedule == scheduled_tasks.size();
}

bool reference_global_solver::check_problem_compatibility() const
{
	return std::find(m_supported_problem_versions.begin(),
					 m_supported_problem_versions.end(),
					 m_environment.problem_version) != m_supported_problem_versions.end();
}

std::string reference_global_solver::get_solver_name() const
{
	return "reference global solver";
}

global_solver::metadata_map reference_global_solver::get_solver_metadata() const
{
	return metadata_map {};
}