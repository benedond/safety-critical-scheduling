#ifndef _SIMPLE_SOLVER_H
#define _SIMPLE_SOLVER_H

#include "instance.h"

class simple_solver
{
private:
	const Environment& m_environment;
	const std::unordered_map<std::string, Task>& m_tasks;

	bool m_solved, m_feasible;
	std::vector<Window> m_windows;

	Window save_window(Window&& window);
	bool check_feasibility();
	void solve();

public:
	Solution get_solution();

	simple_solver(const Environment& e, const std::unordered_map<std::string, Task>& t);
};

#endif // _SIMPLE_SOLVER_H
