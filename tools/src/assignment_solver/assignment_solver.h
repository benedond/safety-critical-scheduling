#ifndef ASSIGNMENT_SOLVER_H
#define ASSIGNMENT_SOLVER_H

// old ILP
std::vector<task> solve_old(const arg_parser& args,
		                    const environment& e,
		                    const assignment_characteristic_list& assignment_characteristics,
		                    const assignment_cut_list& assignment_cuts);

// minutil-ILP
std::vector<task> solve_utilization(const arg_parser& args,
			                        const environment& e,
			                        const assignment_characteristic_list& assignment_characteristics);

// reference assignment heuristic
std::vector<task> solve_reference(const arg_parser& args,
		                          const environment& e,
		                          const assignment_characteristic_list& assignment_characteristics);

// random resource assignment
std::vector<task> solve_random(const arg_parser& args,
							   const environment& e,
							   const assignment_characteristic_list& assignment_characteristics);

#endif // ASSIGNMENT_SOLVER_H
