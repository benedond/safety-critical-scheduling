#include "instance.h"

Environment parse_environment(const nlohmann::json& json)
{
	Environment e;

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

std::unordered_map<std::string, Task> parse_tasks(const nlohmann::json& json)
{
	std::unordered_map<std::string, Task> t;

	auto& tasks = json["tasks"];
	for (auto& task : tasks)
	{
		std::string name = task["name"];
		auto& processors = task["processors"];

		std::vector<std::string> p;
		for (auto& processor : processors)
		{
			p.push_back((std::string) processor);
		}

		t[name] = { .name = name, .length = task["length"], .processors = std::move(p) };
	}

	return t;
}

Solution parse_solution(const nlohmann::json& json)
{
	Solution s;

	auto& solution = json["solution"];

	auto& windows = solution["windows"];
	for (auto& window : windows)
	{
		std::vector<std::string> t;

		auto& tasks = window["tasks"];
		for (auto& task : tasks)
		{
			t.push_back((std::string) task);
		}

		s.windows.push_back({ .length = window["length"], .tasks = std::move(t) });
	}

	s.feasible = solution["feasible"];

	return s;
}

void write_solution(nlohmann::json& json, const Solution& solution)
{
	auto& json_solution = json["solution"];
	json_solution["feasible"] = solution.feasible;

	int i=0;
	auto& json_windows = json_solution["windows"];

	if (solution.feasible)
	{
		for (auto& w : solution.windows)
		{
			auto& json_window = json_windows[i];
			json_window["length"] = w.length;
			json_window["tasks"] = w.tasks;
			i++;
		}
	}
	else
	{
		json_windows = {};
	}
}
