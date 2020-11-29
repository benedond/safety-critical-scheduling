#include <iostream>
#include <chrono>
#include <unordered_map>
#include <fstream>
#include <gurobi_c++.h>

#include "../common/instance.h"
#include "../common/arg_parser.h"
#include "../common/ilp_util.h"

#define INFEASIBLE_MODEL_FILENAME std::string("infeasible_global_problem")

std::pair<solution, std::vector<task>> solve(const arg_parser& args, const environment& e, const assignment_characteristic_list& assignment_characteristics)
{
	if (e.problem_version != 1)
		throw std::invalid_argument("problem version is not supported");

	std::vector<std::vector<std::vector<GRBVar>>> a;

	GRBEnv env;
	env.set(GRB_IntParam_OutputFlag, 0);
	GRBModel model(env);

	int num_tasks = assignment_characteristics.size();
	int windows_ub = num_tasks;

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
				GRBVar a_ijk = model.addVar(0, 1, assignment_characteristic.energy_consumption, GRB_BINARY, "a" + std::to_string(i) + "," + std::to_string(j) + "," + std::to_string(a_ij.size()));
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
		l[j] = model.addVar(0, GRB_INFINITY, 1, GRB_INTEGER, "l" + std::to_string(j));

		window_length_sum += l[j];

		for (int i = 0; i < num_tasks; i++)
		{
			auto& task = assignment_characteristics[i];
			int k = 0;
			for (auto& assignment_characteristic : task.resource_assignments)
				model.addConstr(l[j] >= (a[i][j][k++] * assignment_characteristic.length) / 0.6, task.task + " is at most 60% of l" + std::to_string(j));
		}

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

			for (int i=0; i<num_tasks; i++)
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

	auto start = std::chrono::high_resolution_clock::now();
	model.optimize();
	auto end = std::chrono::high_resolution_clock::now();

	solution s{ .solver_name = "ILP Solver (global)",
			.solution_time = (uint64_t)std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() };
	std::vector<task> tasks;

	if (model.get(GRB_IntAttr_Status) == GRB_OPTIMAL)
	{
		s.feasible = true;

		for (int j = 0; j < windows_ub; j++)
		{
			int window_length = (int)l[j].get(GRB_DoubleAttr_X);
			if (window_length < 1)
				continue;

			std::unordered_map<std::string, int> pu_allocations;
			window win { .length = window_length };

			for (int i = 0; i < num_tasks; i++)
			{
				auto& task_characteristic = assignment_characteristics[i];
				task task_definition { .name = task_characteristic.task, .command = task_characteristic.command };
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
		bool iis_output = !args.is_arg_present("--no-iis-output");
		if (iis_output)
		{
			model.computeIIS();
			write_iis(INFEASIBLE_MODEL_FILENAME, model);
		}
	}

	return std::make_pair(s, tasks);
}

int main(int argc, char** argv)
{
	arg_parser args(argc, argv);
	nlohmann::json json;

	std::string input_filename = args.get_arg_value("--input");
	if (!input_filename.empty())
	{
		if (!read_json_from_file(json, input_filename))
			return EXIT_FAILURE;
	}
	else
	{
		std::cin >> json;
	}

	environment environment;
	assignment_characteristic_list assignment_characteristics;

	bool solution_feasible = false;
	try
	{
		environment = parse_environment(json);
		assignment_characteristics = parse_assignment_characteristics(json);
	}
	catch (const nlohmann::detail::parse_error& error)
	{
		std::cerr << "failed to parse input json: " << error.what() << std::endl;
		return EXIT_FAILURE;
	}

	try
	{
		auto sol = solve(args, environment, assignment_characteristics);
		write_tasks(json, sol.second);
		write_solution(json, sol.first);
		solution_feasible = sol.first.feasible;
	}
	catch (const std::invalid_argument& error)
	{
		std::cerr << "argument error: " << error.what() << std::endl;
		return EXIT_FAILURE;
	}

	std::string output_filename = args.get_arg_value("--output");
	if (!output_filename.empty())
	{
		if (!write_json_to_file(json, output_filename))
			return EXIT_FAILURE;
	}
	else
	{
		std::cout << json;
	}

	return solution_feasible ? EXIT_SUCCESS : EXIT_INFEASIBLE_SOLUTION;
}
