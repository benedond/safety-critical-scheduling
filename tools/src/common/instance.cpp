#include <iostream>
#include <fstream>

#include "instance.h"

environment parse_environment(const nlohmann::json& json)
{
	environment e;

	auto& env = json["environment"];

	auto& processors = env["processors"];
	for (auto& processor : processors)
	{
		std::string json_type = processor["type"];
		std::string name = processor["name"];
		processor_type type = processor_type::invalid_type;

		if (json_type == "main_processor")
			type = processor_type::main_processor;
		else if (json_type == "coprocessor")
			type = processor_type::coprocessor;

		e.processors[name] = { .name = name, .processing_units = processor["processingUnits"], .type = type };
		e.processors_list.push_back(&e.processors.at(name));
	}

	e.major_frame_length = env["majorFrameLength"];
	e.problem_version = env["problemVersion"];

	return e;
}

task_map parse_tasks(const nlohmann::json& json)
{
	task_map t;

	auto& tasks = json["tasks"];
	for (auto& task : tasks)
	{
		std::string name = task["name"];
		auto& processor_assignments = task["processors"];

		std::vector<task::processor_assignment> pas;
		for (auto& processor_assignment : processor_assignments)
			pas.push_back({ .processor = processor_assignment["processor"],
							.processing_units = processor_assignment["processingUnits"] });

		t[name] = { .name = name, .length = task["length"], .assignment_index = task["assignmentIndex"], .processors = std::move(pas) };
	}

	return t;
}

assignment_characteristic_list parse_assignment_characteristics(const nlohmann::json& json)
{
	assignment_characteristic_list ac;

	auto& assignment_characteristics = json["assignmentCharacteristics"];
	for (auto& assignment_char : assignment_characteristics)
	{
		assignment_characteristic a{ .task = assignment_char["task"] };

		auto& resource_assignments = assignment_char["resourceAssignments"];
		for (auto& res_ass : resource_assignments)
		{
			assignment_characteristic::resource_assignment ra{ .energy_consumption = res_ass["energyConsumption"],
																.length = res_ass["length"] };

			auto& processors = res_ass["processors"];
			for (auto& processor : processors)
			{
				ra.processors.push_back({ .processor = processor["processor"],
										  .processing_units = processor["processingUnits"] });
			}

			a.resource_assignments.push_back(std::move(ra));
		}

		ac.push_back(std::move(a));
	}

	return ac;
}

solution parse_solution(const nlohmann::json& json)
{
	solution s;

	auto& solution = json["solution"];

	s.feasible = solution["feasible"];
	s.solver_name = solution["solverName"];
	s.solution_time = solution["solutionTime"];
	auto& metadata = solution["solverMetadata"];

	for (auto itt = metadata.begin(); itt != metadata.end(); itt++)
		s.solver_metadata[itt.key()] = itt.value();

	auto& windows = solution["windows"];
	for (auto& window : windows)
	{
		std::vector<window::task_assignment> tas;

		auto& task_assignments = window["tasks"];
		for (auto& task_assignment : task_assignments)
		{
			tas.push_back({ .task = task_assignment["task"],
							.processor = task_assignment["processor"],
							.processing_unit = task_assignment["processingUnit"],
							.start = task_assignment["start"],
							.length = task_assignment["length"] });
		}

		s.windows.push_back({ .length = window["length"], .task_assignments = std::move(tas) });
	}

	return s;
}

assignment_cut_list parse_assignment_cuts(const nlohmann::json& json)
{
	assignment_cut_list acs;

	auto& assignment_cuts = json["assignmentCuts"];

	for (auto& cut : assignment_cuts)
	{
		std::vector<assignment_cut> a;

		for (auto& assignment : cut)
			a.push_back({ .task = assignment["task"], .assignment_index = assignment["assignmentIndex"] });

		acs.push_back(std::move(a));
	}

	return acs;
}

void write_tasks(nlohmann::json& json, const std::vector<task>& tasks)
{
	auto& json_tasks = json["tasks"];
	json_tasks.clear();

	int i = 0;
	for (auto& task : tasks)
	{
		auto& json_task = json_tasks[i];
		json_task["name"] = task.name;
		json_task["length"] = task.length;
		json_task["assignmentIndex"] = task.assignment_index;

		auto& json_task_processors = json_task["processors"];
		int j = 0;
		for (auto& processor : task.processors)
		{
			auto& json_task_processor = json_task_processors[j];
			json_task_processor["processor"] = processor.processor;
			json_task_processor["processingUnits"] = processor.processing_units;
			j++;
		}

		i++;
	}
}

void write_solution(nlohmann::json& json, const solution& solution)
{
	auto& json_solution = json["solution"];
	json_solution.clear();

	json_solution["feasible"] = solution.feasible;
	json_solution["solverName"] = solution.solver_name;
	json_solution["solutionTime"] = solution.solution_time;
	auto& json_solver_metadata = json_solution["solverMetadata"];

	for (auto& item : solution.solver_metadata)
		json_solver_metadata[item.first] = item.second;

	int i = 0;
	auto& json_windows = json_solution["windows"];

	if (solution.feasible)
	{
		for (auto& w : solution.windows)
		{
			auto& json_window = json_windows[i];
			json_window["length"] = w.length;

			auto& json_tasks = json_window["tasks"];
			int j = 0;
			for (auto& task_assignment : w.task_assignments)
			{
				auto& json_task = json_tasks[j];
				json_task["task"] = task_assignment.task;
				json_task["processor"] = task_assignment.processor;
				json_task["processingUnit"] = task_assignment.processing_unit;
				json_task["start"] = task_assignment.start;
				json_task["length"] = task_assignment.length;
				j++;
			}

			i++;
		}
	}
	else
	{
		json_windows = {};
	}
}

bool read_json_from_file(nlohmann::json& json, const std::string& filename)
{
	std::ifstream input_file(filename);
	if (!input_file.is_open())
	{
		std::cerr << "failed to open input file " << filename << " for reading" << std::endl;
		return false;
	}

	input_file >> json;
	return true;
}

bool write_json_to_file(const nlohmann::json& json, const std::string& filename)
{
	std::ofstream output_file(filename);
	if (!output_file.is_open())
	{
		std::cerr << "failed to open output file " << filename << " for writing" << std::endl;
		return false;
	}

	output_file << json;
	return true;
}
