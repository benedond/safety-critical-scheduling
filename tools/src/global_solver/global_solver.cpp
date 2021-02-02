#include <iostream>
#include <chrono>

#include "global_solver.h"

#define NOT_IMPLEMENTED throw std::logic_error("not implemented")

global_solver::global_solver(const environment& e, const assignment_characteristic_list& ac)
		: m_environment(e), m_assignments(ac), m_solved(false), m_feasible(false), m_solution_time(0)
{
}

solution global_solver::get_solution()
{
	if (!m_solved)
	{
		if (!check_problem_compatibility())
			throw std::invalid_argument("problem version is not supported");

		auto start = std::chrono::high_resolution_clock::now();
		solve();
		auto end = std::chrono::high_resolution_clock::now();

		m_solution_time = std::chrono::duration_cast<std::chrono::milliseconds>(end-start).count();
	}

	solution s { .feasible = m_feasible,
			     .solver_name = get_solver_name(),
			     .solution_time = m_solution_time,
			     .solver_metadata = get_solver_metadata() };

	if (m_feasible)
		s.windows = m_windows;

	return s;
}

void global_solver::solve()
{
	NOT_IMPLEMENTED;
}

bool global_solver::check_problem_compatibility() const
{
	NOT_IMPLEMENTED;
}

std::string global_solver::get_solver_name() const
{
	NOT_IMPLEMENTED;
}

global_solver::metadata_map global_solver::get_solver_metadata() const
{
	NOT_IMPLEMENTED;
}

window global_solver::save_window(window&& window)
{
	m_windows.push_back(std::move(window));
	return { .length = -1 };
}

bool global_solver::check_feasibility() const
{
	int total_time = 0;
	for (auto& w : m_windows)
		total_time += w.length;

	if (total_time > m_environment.major_frame_length)
	{
		std::cerr << "solution is infeasible - total_time: " << total_time << " major_frame_length: " << m_environment.major_frame_length << std::endl;
		return false;
	}

	return true;
}
