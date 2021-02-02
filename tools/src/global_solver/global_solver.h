#ifndef SOLVER_H
#define SOLVER_H

#include "../common/instance.h"

class global_solver
{
public:
	typedef std::unordered_map<std::string, std::string> metadata_map;
	solution get_solution();

	global_solver(const environment& e, const assignment_characteristic_list& ac);

protected:
	const environment& m_environment;
	const assignment_characteristic_list& m_assignments;

	bool m_solved, m_feasible;
	std::vector<window> m_windows;

	window save_window(window&& window);
	bool check_feasibility() const;
	virtual void solve();
	virtual bool check_problem_compatibility() const;
	virtual std::string get_solver_name() const;
	virtual metadata_map get_solver_metadata() const;

private:
	uint64_t m_solution_time;
};

#endif // SOLVER_H
