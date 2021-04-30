#ifndef RANDOM_TASK_ORDER_SOLVER_H
#define RANDOM_TASK_ORDER_SOLVER_H

#include "solver.h"

class random_task_order_solver : public solver
{
public:
	random_task_order_solver(const environment& e, const task_map& t);

protected:
	void solve() override;
	bool check_problem_compatibility() const override;
	std::string get_solver_name() const override;
	metadata_map get_solver_metadata() const override;

private:
	const std::unordered_set<int> m_supported_problem_versions{ 1, 2 };
	const int m_seed;
};

#endif // RANDOM_TASK_ORDER_SOLVER_H
