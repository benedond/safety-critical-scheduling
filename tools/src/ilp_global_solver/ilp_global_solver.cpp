#include <iostream>
#include <chrono>
#include <gurobi_c++.h>

#include "../common/instance.h"
#include "../common/arg_parser.h"
#include "../common/ilp_util.h"
#include "ilp_global_solver.h"

#define INFEASIBLE_MODEL_FILENAME std::string("infeasible_global_problem")

// old ILP
std::pair<solution, std::vector<task>> solve_eik(const arg_parser& args, const environment& e, const assignment_characteristic_list& assignment_characteristics)
{
	// leftover model from development
	std::vector<std::vector<std::vector<GRBVar>>> a;

	GRBEnv env;
	GRBModel model(env);

	int num_tasks = assignment_characteristics.size();
	int windows_ub = num_tasks;
	int sense = 1;
	if (args.is_arg_present("--maximize"))
		sense = -1;

	GRBLinExpr energy_consumption_sum;
	for (int i = 0; i < num_tasks; i++)
	{
		auto& task = assignment_characteristics[i];
		std::vector<std::vector<GRBVar>> a_i;
		GRBLinExpr assignment_constraint_expr;

		for (int j = 0; j < windows_ub; j++)
		{
			std::vector<GRBVar> a_ij;

			// k
			for (auto& assignment_characteristic : task.resource_assignments)
			{
				GRBVar a_ijk = model.addVar(0, 1, 0, GRB_BINARY, "a" + std::to_string(i) + "," + std::to_string(j) + "," + std::to_string(a_ij.size()));

				int processor_capacity = 0;
				for (auto& p : assignment_characteristic.processors)
					processor_capacity += e.processors.at(p.processor).processing_units;
				float energy_consumption = assignment_characteristic.slope + (float) assignment_characteristic.intercept / (float) processor_capacity;
				energy_consumption_sum += a_ijk * energy_consumption * assignment_characteristic.length * sense;
				assignment_constraint_expr += a_ijk;
				a_ij.push_back(std::move(a_ijk));
			}

			a_i.push_back(std::move(a_ij));
		}

		model.addConstr(assignment_constraint_expr == 1, task.task + " assigned");
		a.push_back(std::move(a_i));
	}

	std::vector<GRBVar> l(windows_ub);
	GRBLinExpr window_length_sum;
	for (int j = 0; j < windows_ub; j++)
	{
		l[j] = model.addVar(0, GRB_INFINITY, 0, GRB_INTEGER, "l" + std::to_string(j));

		window_length_sum += l[j];

		GRBLinExpr a_ik_sum;
		for (int i = 0; i < num_tasks; i++)
		{
			auto& task = assignment_characteristics[i];
			int k = 0;
			for (auto& assignment_characteristic : task.resource_assignments)
			{
				a_ik_sum += a[i][j][k];
				model.addConstr(l[j] >= (a[i][j][k++] * assignment_characteristic.length) / e.sc_part, task.task + " is at most " + std::to_string(e.sc_part*100) + "% of l" + std::to_string(j));
			}
		}
		model.addConstr(l[j] <= a_ik_sum * e.major_frame_length, "window " + std::to_string(j) + " is not empty");

		if (j > 0)
			model.addConstr(l[j] <= l[j - 1], "window ordering");
	}
	model.addConstr(window_length_sum <= e.major_frame_length, "major frame length");

	// constraint 5(+6)
	for (auto& processor : e.processors_list)
	{
		for (int j = 0; j < windows_ub; j++)
		{
			GRBLinExpr resource_capacity_contraint_expr;

			for (int i = 0; i < num_tasks; i++)
			{
				auto& task = assignment_characteristics[i];

				int k = 0;
				for (auto& assignment_characteristic : task.resource_assignments)
				{
					for (auto& acp : assignment_characteristic.processors)
					{
						if (acp.processor == processor->name)
						{
							resource_capacity_contraint_expr += a[i][j][k] * acp.processing_units;
						}
					}
					k++;
				}
			}

			model.addConstr(resource_capacity_contraint_expr <= processor->processing_units, processor->name + " capacity (window " + std::to_string(j) + ")");
		}
	}

	model.setObjectiveN(energy_consumption_sum, 0, 1, 1.0, 0.0, 0.0, "min energy consumption");

	if (args.is_arg_present("--optimize-schedule"))
		model.setObjectiveN(window_length_sum, 1, 0, 1.0, 0.0, 0.0, "min total schedule length");

	auto start = std::chrono::high_resolution_clock::now();
	model.optimize();
	auto end = std::chrono::high_resolution_clock::now();

	solution s{ .solver_name = "ILP Solver (global):eik",
			.solution_time = (uint64_t)std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() };
	std::vector<task> tasks;

	if (model.get(GRB_IntAttr_Status) == GRB_OPTIMAL || model.get(GRB_IntAttr_Status) == GRB_TIME_LIMIT)
	{
		s.feasible = true;

		for (int j = 0; j < windows_ub; j++)
		{
			int window_length = (int)l[j].get(GRB_DoubleAttr_X);
			if (window_length < 1)
				continue;

			std::unordered_map<std::string, int> pu_allocations;
			window win{ .length = window_length };

			for (int i = 0; i < num_tasks; i++)
			{
				auto& task_characteristic = assignment_characteristics[i];
				task task_definition{ .name = task_characteristic.task, .command = task_characteristic.command };
				bool push_task = false;

				int k = 0, aix = 0;
				for (auto& assignment_characteristic : task_characteristic.resource_assignments)
				{
					if (a[i][j][k++].get(GRB_DoubleAttr_X) > 0.5)
					{
						for (auto& p : assignment_characteristic.processors)
						{
							win.task_assignments.push_back({ .task = task_characteristic.task,
																   .processor = p.processor,
																   .processing_unit = pu_allocations[p.processor],
																   .start = 0, .length = assignment_characteristic.length });
							pu_allocations[p.processor] = pu_allocations[p.processor] + p.processing_units;

							push_task = true;
							task_definition.processors.push_back({ .processor = p.processor, .processing_units = p.processing_units });
							task_definition.length = assignment_characteristic.length;
							task_definition.assignment_index = aix;
						}
					}
					aix++;
				}

				if (push_task)
					tasks.push_back(std::move(task_definition));
			}

			s.windows.push_back(std::move(win));
		}
	}
	else
	{
		s.feasible = false;
		bool iis_output = args.is_arg_present("--iis-output");
		if (iis_output)
		{
			model.computeIIS();
			write_iis(INFEASIBLE_MODEL_FILENAME, model);
		}
	}

	return std::make_pair(std::move(s), std::move(tasks));
}

// global-ILP
std::pair<solution, std::vector<task>> solve_global_ILP(const arg_parser& args, const environment& e, const assignment_characteristic_list& assignment_characteristics)
{
	// global-ILP model model
	int num_tasks = assignment_characteristics.size();
	int windows_ub = num_tasks;
	int sense = 1;
	if (args.is_arg_present("--maximize"))
		sense = -1;

	std::vector<std::vector<std::vector<GRBVar>>> x;

	GRBEnv env;
	GRBModel model(env);

	// x_ijk variables
	for (int i = 0; i < num_tasks; i++)
	{
		auto& task = assignment_characteristics[i];
		std::vector<std::vector<GRBVar>> x_i;
		GRBLinExpr assignment_constraint_expr;

		for (int j = 0; j < windows_ub; j++)
		{
			std::vector<GRBVar> x_ij;

			// task assignment constraint
			for (auto& assignment_characteristic : task.resource_assignments)
			{
				GRBVar x_ijk = model.addVar(0, 1, 0, GRB_BINARY, "x" + std::to_string(i) + "," + std::to_string(j) + "," + std::to_string(x_ij.size()));
				assignment_constraint_expr += x_ijk;
				x_ij.push_back(std::move(x_ijk));
			}

			x_i.push_back(std::move(x_ij));
		}

		model.addConstr(assignment_constraint_expr == 1, task.task + " assigned");
		x.push_back(std::move(x_i));
	}

	// l_j variables
	std::vector<GRBVar> l(windows_ub);
	GRBLinExpr window_length_sum;
	for (int j = 0; j < windows_ub; j++)
	{
		l[j] = model.addVar(0, GRB_INFINITY, 0, GRB_INTEGER, "l" + std::to_string(j));

		window_length_sum += l[j];

		GRBLinExpr a_ik_sum;
		for (int i = 0; i < num_tasks; i++)
		{
			auto& task = assignment_characteristics[i];
			int k = 0;
			for (auto& assignment_characteristic : task.resource_assignments)
			{
				a_ik_sum += x[i][j][k];
				// sc part constraint
				model.addConstr(l[j] >= (x[i][j][k++] * assignment_characteristic.length) / e.sc_part, task.task + " is at most " + std::to_string(e.sc_part*100) + "% of l" + std::to_string(j));
			}
		}

		// window length constraint
		model.addConstr(l[j] <= a_ik_sum * e.major_frame_length, "window " + std::to_string(j) + " is not empty");

		// window ordering constraint
		if (j > 0)
			model.addConstr(l[j] <= l[j - 1], "window ordering");
	}
	// major frame length constraint
	model.addConstr(window_length_sum <= e.major_frame_length, "major frame length");

	// A_ijk variables (=x_ijk*p_ik*a_ik), objective function
	GRBLinExpr energy_consumption_sum;
	for (int i = 0; i < num_tasks; i++)
	{
		auto& task = assignment_characteristics[i];

		for (int j = 0; j < windows_ub; j++)
		{
			int k = 0;
			for (auto& assignment_characteristic : task.resource_assignments)
			{
				auto& x_ijk = x[i][j][k];
				GRBVar A_ijk = model.addVar(0, GRB_INFINITY, 0, GRB_CONTINUOUS, "A" + std::to_string(i) + "," + std::to_string(j) + "," + std::to_string(k));
				model.addConstr(A_ijk == x_ijk * assignment_characteristic.slope * assignment_characteristic.length);
				energy_consumption_sum += A_ijk;
				k++;
			}
		}
	}

	// resource capacity constraint
	for (auto& processor : e.processors_list)
	{
		for (int j = 0; j < windows_ub; j++)
		{
			GRBLinExpr resource_capacity_contraint_expr;

			for (int i = 0; i < num_tasks; i++)
			{
				auto& task = assignment_characteristics[i];

				int k = 0;
				for (auto& assignment_characteristic : task.resource_assignments)
				{
					for (auto& acp : assignment_characteristic.processors)
					{
						if (acp.processor == processor->name)
						{
							resource_capacity_contraint_expr += x[i][j][k] * acp.processing_units;
						}
					}
					k++;
				}
			}

			model.addConstr(resource_capacity_contraint_expr <= processor->processing_units, processor->name + " capacity (window " + std::to_string(j) + ")");
		}
	}

	// B_ijk variables
	for (int j = 0; j < windows_ub; j++)
	{
		std::vector<GRBVar> B_j;
		for (auto& processor : e.processors_list)
		{
			for (int i = 0; i < num_tasks; i++)
			{
				auto& task = assignment_characteristics[i];
				int k = 0;
				for (auto& assignment_characteristic : task.resource_assignments)
				{
					for (auto& acp : assignment_characteristic.processors)
					{
						if (acp.processor == processor->name)
						{

							GRBVar B_ijk = model.addVar(0, GRB_INFINITY, 0, GRB_CONTINUOUS, "B_" + std::to_string(i) + "," + std::to_string(j) + "," + processor->name);

							model.addGenConstrIndicator(x[i][j][k], 1, B_ijk == e.sc_part * assignment_characteristic.intercept * l[j], "B_ijkVALUE(" + std::to_string(i) + "," + std::to_string(j) + "," + processor->name + ")");
							if (sense == -1)
								model.addGenConstrIndicator(x[i][j][k], 0, B_ijk == 0, "B_ijkVALUE(" + std::to_string(i) + "," + std::to_string(j) + "," + processor->name + ")_BOUND");
							B_j.push_back(std::move(B_ijk));
						}
					}
					k++;
				}
			}
		}

		GRBVar B_j_max = model.addVar(0, GRB_INFINITY, 0, GRB_CONTINUOUS, "B_" + std::to_string(j) + "_max");
		model.addGenConstrMax(B_j_max, B_j.data(), B_j.size(), 0, "B_" + std::to_string(j) + "_max_constr");
		energy_consumption_sum += B_j_max;
	}

	// minimize (default)/maximize objective
	if (sense == 1)
		model.setObjectiveN(energy_consumption_sum * 1.0f/(float) e.major_frame_length, 0, 1, 1.0, 0.0, 0.0, "min avg power consumption");
	else
		model.setObjective(energy_consumption_sum * 1.0f/(float) e.major_frame_length, GRB_MAXIMIZE);

	// enable C_max (schedule length) optimization (not recommended for global_ilp, leftover from development)
	if (args.is_arg_present("--optimize-schedule"))
	{
		if (sense == 1)
		{
			std::cerr << "warning: --optimize-schedule active with predictor method" << std::endl;
			model.setObjectiveN(window_length_sum, 1, 0, 1.0, 0.0, 0.0, "min total schedule length");
		}
		else if (sense == -1)
		{
			std::cerr << "error: --optimize-schedule is not compatible with --maximize while using predictor method, disregarding" << std::endl;
		}
	}

	// optimize the model
	auto start = std::chrono::high_resolution_clock::now();
	model.optimize();
	auto end = std::chrono::high_resolution_clock::now();

	solution s{ .solver_name = "ILP Solver (global):predictor",
			.solution_time = (uint64_t)std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() };
	std::vector<task> tasks;

	if (model.get(GRB_IntAttr_Status) == GRB_OPTIMAL || (model.get(GRB_IntAttr_Status) == GRB_TIME_LIMIT && model.get(GRB_IntAttr_SolCount) > 0))
	{
		// feasible solution
		s.feasible = true;

		for (int j = 0; j < windows_ub; j++)
		{
			int window_length = (int)l[j].get(GRB_DoubleAttr_X);
			if (window_length < 1)
				continue;

			std::unordered_map<std::string, int> pu_allocations;
			window win{ .length = window_length };

			for (int i = 0; i < num_tasks; i++)
			{
				auto& task_characteristic = assignment_characteristics[i];
				task task_definition{ .name = task_characteristic.task, .command = task_characteristic.command };
				bool push_task = false;

				int k = 0, aix = 0;
				for (auto& assignment_characteristic : task_characteristic.resource_assignments)
				{
					if (x[i][j][k++].get(GRB_DoubleAttr_X) > 0.5)
					{
						for (auto& p : assignment_characteristic.processors)
						{
							win.task_assignments.push_back({ .task = task_characteristic.task,
																   .processor = p.processor,
																   .processing_unit = pu_allocations[p.processor],
																   .start = 0, .length = assignment_characteristic.length });
							pu_allocations[p.processor] = pu_allocations[p.processor] + p.processing_units;

							push_task = true;
							task_definition.processors.push_back({ .processor = p.processor, .processing_units = p.processing_units });
							task_definition.length = assignment_characteristic.length;
							task_definition.assignment_index = aix;
						}
					}
					aix++;
				}

				if (push_task)
					tasks.push_back(std::move(task_definition));
			}

			s.windows.push_back(std::move(win));
		}
	}
	else
	{
		// infeasible solution
		s.feasible = false;
		bool iis_output = args.is_arg_present("--iis-output");
		if (iis_output)
		{
			model.computeIIS();
			write_iis(INFEASIBLE_MODEL_FILENAME, model);
		}
	}

	return std::make_pair(std::move(s), std::move(tasks));
}

std::pair<solution, std::vector<task>> solve(const arg_parser& args, const environment& e, const assignment_characteristic_list& assignment_characteristics)
{
	if (args.is_arg_present("--method"))
	{
		auto method = args.get_arg_value("--method");

		if (method == "global-ILP") return solve_global_ILP(args, e, assignment_characteristics);
		else if (method == "eik") return solve_eik(args, e, assignment_characteristics);
		else std::cerr << "optimization method not recognized, using default of global-ILP instead" << std::endl;
	}

	return solve_global_ILP(args, e, assignment_characteristics);
}