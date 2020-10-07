#include "instance.h"

environment parse_environment(const nlohmann::json& json)
{
	environment e;

	auto& env = json["environment"];

	auto& processors = env["processors"];
	for (auto& processor : processors)
	{
		std::string name = processor["name"];
		e.processors[name] = { .name = name, .processing_units = processor["processingUnits"] };
	}

	e.main_frame_length = env["mainFrameLength"];

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

		t[name] = { .name = name, .length = task["length"], .processors = std::move(pas) };
	}

	return t;
}

solution parse_solution(const nlohmann::json& json)
{
	solution s;

	auto& solution = json["solution"];

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

	s.feasible = solution["feasible"];

	return s;
}

void write_solution(nlohmann::json& json, const solution& solution)
{
	auto& json_solution = json["solution"];
	json_solution["feasible"] = solution.feasible;

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
