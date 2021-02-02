#ifndef RANDOM_TASK_ORDER_SOLVER_H
#define RANDOM_TASK_ORDER_SOLVER_H

#include "global_solver.h"

class random_global_solver : public global_solver
{
public:
	random_global_solver(const environment& e, const assignment_characteristic_list& t);

protected:
	void solve() override;
	bool check_problem_compatibility() const override;
	std::string get_solver_name() const override;
	metadata_map get_solver_metadata() const override;

private:
	const std::array<int, 2> m_supported_problem_versions{ 1, 2 };
	const int m_seed;
};

#endif // RANDOM_TASK_ORDER_SOLVER_H
