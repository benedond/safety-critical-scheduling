#ifndef LONGEST_TASKS_FIRST_SOLVER_H
#define LONGEST_TASKS_FIRST_SOLVER_H

#include "solver.h"

class longest_tasks_first_solver : public solver
{
public:
	longest_tasks_first_solver(const environment& e, const task_map& t);

protected:
	void solve() override;
	bool check_problem_compatibility() const override;
	std::string get_solver_name() const override;
	metadata_map get_solver_metadata() const override;

private:
	const std::unordered_set<int> m_supported_problem_versions{ 1, 2 };
	int m_out_of_order_task_count;
};

#endif // LONGEST_TASKS_FIRST_SOLVER_H
