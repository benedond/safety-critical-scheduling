#ifndef _SIMPLE_SOLVER_H
#define _SIMPLE_SOLVER_H

#include "../common/instance.h"

class simple_solver
{
private:
	const environment& m_environment;
	const task_map& m_tasks;

	bool m_solved, m_feasible;
	std::vector<window> m_windows;

	window save_window(window&& window);
	bool check_feasibility();
	void solve();

public:
	solution get_solution();

	simple_solver(const environment& e, const task_map& t);
};

#endif // _SIMPLE_SOLVER_H
