#include <iostream>
#include <chrono>

#include "solver.h"

#define NOT_IMPLEMENTED throw std::logic_error("not implemented")

solver::solver(const environment& e, const task_map& t)
		: m_environment(e), m_tasks(t), m_solved(false), m_feasible(false), m_solution_time(0)
{
}

solution solver::get_solution()
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

void solver::solve()
{
	NOT_IMPLEMENTED;
}

bool solver::check_problem_compatibility() const
{
	NOT_IMPLEMENTED;
}

std::string solver::get_solver_name() const
{
	NOT_IMPLEMENTED;
}

solver::metadata_map solver::get_solver_metadata() const
{
	NOT_IMPLEMENTED;
}

window solver::save_window(window&& window)
{
	m_windows.push_back(std::move(window));
	return { .length = -1 };
}

bool solver::check_feasibility() const
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
