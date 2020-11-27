#ifndef ILP_UTIL_H
#define ILP_UTIL_H

#include <gurobi_c++.h>

#define EXIT_INFEASIBLE_SOLUTION 2

void write_iis(const std::string& filename, GRBModel& model);

#endif // ILP_UTIL_H
