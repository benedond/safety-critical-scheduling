#ifndef ILP_GLOBAL_SOLVER_H
#define ILP_GLOBAL_SOLVER_H

// old ILP
std::pair<solution, std::vector<task>> solve_eik(const arg_parser& args,
										         const environment& e,
										         const assignment_characteristic_list& assignment_characteristics);

// global-ILP
std::pair<solution, std::vector<task>> solve_global_ILP(const arg_parser& args,
		                                                const environment& e,
		                                                const assignment_characteristic_list& assignment_characteristics);

std::pair<solution, std::vector<task>> solve(const arg_parser& args,
		                                     const environment& e,
		                                     const assignment_characteristic_list& assignment_characteristics);

#endif // ILP_GLOBAL_SOLVER_H
