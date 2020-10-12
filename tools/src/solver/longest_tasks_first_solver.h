#ifndef SIMPLE_SOLVER_H
#define SIMPLE_SOLVER_H

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
	const std::array<int, 1> m_supported_problem_versions{ 1 };
	int m_out_of_order_task_count;
};

#endif // SIMPLE_SOLVER_H
