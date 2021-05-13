#include <gurobi_c++.h>
#include <set>
#include <map>
#include <random>
#include <chrono>
#include <unordered_set>
#include <unordered_map>

#include "../common/instance.h"
#include "../common/arg_parser.h"
#include "../common/ilp_util.h"
#include "assignment_solver.h"

#define INFEASIBLE_MODEL_FILENAME std::string("infeasible_res_assignment")

// feasible-schedule-ILP
static bool feasible_schedule_exists(const arg_parser& args,
							  		 const environment& e,
							  		 const assignment_characteristic_list& assignment_characteristics,
							  		 const std::vector<task>& assigned_tasks)
{
	// feasible-schedule-ILP model
	std::vector<std::vector<std::vector<GRBVar>>> x;
	std::unordered_map<std::string, int> task_index_map;

	GRBEnv env;
	GRBModel model(env);

	int num_tasks = assignment_characteristics.size();
	int windows_ub = num_tasks;

	// x_ijk variables
	for (int i = 0; i < num_tasks; i++)
	{
		auto& task = assignment_characteristics[i];
		std::vector<std::vector<GRBVar>> x_i;
		GRBLinExpr assignment_constraint_expr;
		task_index_map[task.task] = i;

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
				model.addConstr(l[j] >= (x[i][j][k++] * assignment_characteristic.length) / e.sc_part, task.task + " is at most " + std::to_string(e.sc_part * 100) + "% of l" + std::to_string(j));
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

	// fixed assignments
	for (auto& assignment : assigned_tasks)
	{
		int i = task_index_map[assignment.name];
		int k = assignment.assignment_index;
		GRBLinExpr assignment_constr;

		for (int j=0; j<windows_ub; j++)
			assignment_constr += x[i][j][k];

		model.addConstr(assignment_constr == 1);
	}

	model.optimize();

	if (model.get(GRB_IntAttr_Status) == GRB_OPTIMAL || (model.get(GRB_IntAttr_Status) == GRB_TIME_LIMIT && model.get(GRB_IntAttr_SolCount) > 0))
	{
		// feasible solution exists
		return true;
	}
	else
	{
		// feasible solution does not exist
		bool iis_output = args.is_arg_present("--iis-output");
		if (iis_output)
		{
			model.computeIIS();
			write_iis(INFEASIBLE_MODEL_FILENAME, model);
		}
		return false;
	}
}

// old ILP
std::vector<task> solve_old(const arg_parser& args,
							const environment& e,
							const assignment_characteristic_list& assignment_characteristics,
							const assignment_cut_list& assignment_cuts)
{
	// leftover model from development
	if (e.problem_version != 1)
		throw std::invalid_argument("problem version is not supported");

	std::vector<std::vector<GRBVar>> a;
	std::unordered_map<std::string, int> task_index_map;

	GRBEnv env;
	GRBModel model(env);

	int ix = 0;
	for (auto& task : assignment_characteristics)
	{
		task_index_map[task.task] = ix++;

		std::vector<GRBVar> a_i;
		GRBLinExpr assignment_constraint_expr;

		for (auto& assignment_characteristic : task.resource_assignments)
		{
			int processor_capacity = 0;
			for (auto& p : assignment_characteristic.processors)
				processor_capacity += e.processors.at(p.processor).processing_units;
			float energy_consumption = assignment_characteristic.slope + (float)assignment_characteristic.intercept / (float)processor_capacity;

			GRBVar a_ik = model.addVar(0, 1, energy_consumption, GRB_BINARY, "a" + std::to_string(ix - 1) + "," + std::to_string(a_i.size()));
			assignment_constraint_expr += a_ik;
			a_i.push_back(std::move(a_ik));
		}

		model.addConstr(assignment_constraint_expr == 1, task.task + " assigned");
		a.push_back(std::move(a_i));
	}

	// constraint 3(+4)
	for (auto& processor : e.processors_list)
	{
		GRBLinExpr resource_capacity_contraint_expr;

		int i = 0;
		for (auto& task : assignment_characteristics)
		{
			int k = 0;
			for (auto& assignment_characteristic : task.resource_assignments)
			{
				for (auto& acp : assignment_characteristic.processors)
				{
					if (acp.processor == processor->name)
					{
						resource_capacity_contraint_expr += a[i][k] * acp.processing_units * assignment_characteristic.length;
					}
				}
				k++;
			}
			i++;
		}

		model.addConstr(resource_capacity_contraint_expr <= e.major_frame_length * processor->processing_units, processor->name + " capacity (relaxed)");
	}

	for (auto& assignment_cut : assignment_cuts)
	{
		GRBLinExpr assignment_cut_constraint;

		for (auto& assignment : assignment_cut)
		{
			int task_index = task_index_map[assignment.task];
			assignment_cut_constraint += a[task_index][assignment.assignment_index];
		}

		model.addConstr(assignment_cut_constraint <= assignment_cut.size() - 1, "assignment cut");
	}

	model.optimize();

	std::vector<task> tasks;
	if (model.get(GRB_IntAttr_Status) == GRB_OPTIMAL || model.get(GRB_IntAttr_Status) == GRB_TIME_LIMIT)
	{
		for (size_t i = 0; i < assignment_characteristics.size(); i++)
		{
			int used_assignment_ix = 0;
			for (auto& a_ik : a[i])
			{
				if (a_ik.get(GRB_DoubleAttr_X) > 0.5)
					break;

				used_assignment_ix++;
			}

			auto& t = assignment_characteristics[i];
			auto& c = t.resource_assignments[used_assignment_ix];
			tasks.push_back({ .name = t.task, .command = t.command, .length = c.length, .assignment_index = used_assignment_ix, .processors = c.processors });
		}
	}
	else
	{
		bool iis_output = args.is_arg_present("--iis-output");
		if (iis_output)
		{
			model.computeIIS();
			write_iis(INFEASIBLE_MODEL_FILENAME, model);
		}
	}

	return tasks;
}

// minutil-ILP
std::vector<task> solve_utilization(const arg_parser& args,
									const environment& e,
									const assignment_characteristic_list& assignment_characteristics)
{
	// minutil-ILP model
	std::vector<std::vector<std::vector<GRBVar>>> x;

	GRBEnv env;
	GRBModel model(env);

	int num_tasks = assignment_characteristics.size();
	int windows_ub = num_tasks;

	// minimize (default)/maximize objective
	int sense = 1;
	if (args.is_arg_present("--maximize"))
		sense = -1;

	// x_ijk variables, objective function
	GRBLinExpr processing_time_sum;
	for (int i = 0; i < num_tasks; i++)
	{
		auto& task = assignment_characteristics[i];
		std::vector<std::vector<GRBVar>> x_i;
		GRBLinExpr assignment_constraint_expr;

		for (int j = 0; j < windows_ub; j++)
		{
			std::vector<GRBVar> x_ij;

			// task assigned constraint
			for (auto& assignment_characteristic : task.resource_assignments)
			{
				GRBVar x_ijk = model.addVar(0, 1, 0, GRB_BINARY, "x" + std::to_string(i) + "," + std::to_string(j) + "," + std::to_string(x_ij.size()));

				processing_time_sum += x_ijk * assignment_characteristic.length * sense;
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
				model.addConstr(l[j] >= (x[i][j][k++] * assignment_characteristic.length) / e.sc_part, task.task + " is at most " + std::to_string(e.sc_part * 100) + "% of l" + std::to_string(j));
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

	// resource capacity constraint
	for (auto& processor : e.processors_list)
	{
		for (int j = 0; j < windows_ub; j++)
		{
			GRBLinExpr resource_capacity_constraint_expr;

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
							resource_capacity_constraint_expr += x[i][j][k] * acp.processing_units;
						}
					}
					k++;
				}
			}

			model.addConstr(resource_capacity_constraint_expr <= processor->processing_units, processor->name + " capacity (window " + std::to_string(j) + ")");
		}
	}

	// enable C_max (schedule length) optimization
	model.setObjectiveN(processing_time_sum, 0, 1, 1.0, 0.0, 0.0, "optimize utilization");

	if (args.is_arg_present("--optimize-schedule"))
		model.setObjectiveN(window_length_sum, 1, 0, 1.0, 0.0, 0.0, "min total schedule length");

	// optimize the model
	model.optimize();

	std::vector<task> tasks;

	if (model.get(GRB_IntAttr_Status) == GRB_OPTIMAL || (model.get(GRB_IntAttr_Status) == GRB_TIME_LIMIT && model.get(GRB_IntAttr_SolCount) > 0))
	{
		// feasible solution
		for (int j = 0; j < windows_ub; j++)
		{
			int window_length = (int)l[j].get(GRB_DoubleAttr_X);
			if (window_length < 1)
				continue;

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
		}
	}
	else
	{
		// infeasible solution
		bool iis_output = args.is_arg_present("--iis-output");
		if (iis_output)
		{
			model.computeIIS();
			write_iis(INFEASIBLE_MODEL_FILENAME, model);
		}
	}

	return tasks;
}

// reference assignment heuristic
std::vector<task> solve_reference(const arg_parser& args,
								  const environment& e,
								  const assignment_characteristic_list& assignment_characteristics)
{
	// reference assignment heuristic
	std::vector<task> tasks;

	std::set<simple_task_assignment, std::greater<>> tasks_to_schedule;
	std::unordered_map<std::string, std::set<simple_task_assignment, std::less<>>> possible_task_assignments;
	std::unordered_set<std::string> assigned_tasks;

	for (auto& ac : assignment_characteristics)
	{
		int i=0;
		for (auto& ra : ac.resource_assignments)
		{
			simple_task_assignment ta = {.task = ac.task,
					.command = ac.command,
					.slope = ra.slope,
					.intercept = ra.intercept,
					.length = ra.length,
					.assignment_index = i++,
					.processors = ra.processors};

			possible_task_assignments[ac.task].insert(ta);
			tasks_to_schedule.insert(std::move(ta));
		}
	}

	tasks.reserve(assignment_characteristics.size());
	for (auto& task : tasks_to_schedule)
	{
		if (assigned_tasks.find(task.task) != assigned_tasks.end())
			continue;

		bool assignment_accepted = false;

		for (auto& assignment : possible_task_assignments[task.task])
		{
			tasks.push_back({ .name = assignment.task,
									.command = assignment.command,
									.length = assignment.length,
									.assignment_index = assignment.assignment_index,
									.processors = assignment.processors });

			if (feasible_schedule_exists(args, e, assignment_characteristics, tasks))
			{
				// ACCEPT ASSIGNMENT
				assigned_tasks.insert(task.task);
				assignment_accepted = true;
				break;
			}
			else
			{
				// REJECT ASSIGNMENT
				tasks.pop_back();
			}
		}

		if (!assignment_accepted)
			break;
	}

	assert(assigned_tasks.size() <= assignment_characteristics.size());
	assert(assigned_tasks.size() == tasks.size());

	// infeasible resource assignment
	if (tasks.size() != assignment_characteristics.size())
	{
		tasks.clear();
		assert(tasks.empty());
	}

	return tasks;
}

// random resource assignment
std::vector<task> solve_random(const arg_parser& args, const environment& e, const assignment_characteristic_list& assignment_characteristics)
{
	std::vector<const assignment_characteristic*> tasks_to_assign;
	tasks_to_assign.reserve(assignment_characteristics.size());
	for (auto& task : assignment_characteristics)
		tasks_to_assign.push_back(&task);

	std::mt19937 random_generator(std::chrono::high_resolution_clock::now().time_since_epoch().count());
	std::shuffle(tasks_to_assign.begin(), tasks_to_assign.end(), random_generator);

	std::uniform_int_distribution<> assignment_dist(0, 99);

	std::vector<task> tasks;
	while (!tasks_to_assign.empty())
	{
		auto task = tasks_to_assign.back();
		tasks_to_assign.pop_back();

		int sel_assignment = assignment_dist(random_generator) % (int) task->resource_assignments.size();
		auto& assignment = task->resource_assignments[sel_assignment];

		tasks.push_back({ .name = task->task,
								  .command = task->command,
								  .length = assignment.length,
								  .assignment_index = sel_assignment,
								  .processors = assignment.processors });

	}

	return tasks;
}