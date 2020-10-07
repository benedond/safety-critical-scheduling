#ifndef _INSTANCE_H
#define _INSTANCE_H

#include <string>
#include <vector>
#include <unordered_map>
#include <nlohmann/json.hpp>

struct processor
{
	std::string name;
	int processing_units;
};

struct environment
{
	std::unordered_map<std::string, processor> processors;
	int main_frame_length;
};

struct task
{
	struct processor_assignment
	{
		std::string processor;
		int processing_units;
	};

	std::string name;
	int length;
	std::vector<processor_assignment> processors;
};

struct window
{
	struct task_assignment
	{
		std::string task, processor;
		int processing_unit;
		int start, length;
	};

	int length;
	std::vector<task_assignment> task_assignments;
};

struct solution
{
	bool feasible;
	std::vector<window> windows;
};

typedef std::unordered_map<std::string, task> task_map;

environment parse_environment(const nlohmann::json& json);
task_map parse_tasks(const nlohmann::json& json);
solution parse_solution(const nlohmann::json& json);

void write_solution(nlohmann::json& json, const solution& solution);

#endif // _INSTANCE_H
