#ifndef INSTANCE_H
#define INSTANCE_H

#include <string>
#include <vector>
#include <unordered_map>
#include <cstdint>
#include <nlohmann/json.hpp>

enum class processor_type
{
	invalid_type,
	main_processor,
	coprocessor
};

struct processor
{
	std::string name;
	int processing_units;
	processor_type type;
};

struct environment
{
	std::unordered_map<std::string, processor> processors;
	std::vector<processor*> processors_list;
	int major_frame_length;
	int problem_version;
};

struct task
{
	struct processor_assignment
	{
		std::string processor;
		int processing_units;
	};

	std::string name;
	std::string command;
	int length;
	int assignment_index;
	std::vector<processor_assignment> processors;
};

struct assignment_characteristic
{
	struct resource_assignment
	{
		float energy_consumption;
		int length;
		std::vector<task::processor_assignment> processors;
	};

	std::string task;
	std::string command;
	std::vector<resource_assignment> resource_assignments;
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
	std::string solver_name;
	uint64_t solution_time;
	std::unordered_map<std::string, std::string> solver_metadata;
	std::vector<window> windows;
};

struct assignment_cut
{
	std::string task;
	int assignment_index;
};

typedef std::unordered_map<std::string, task> task_map;
typedef std::vector<assignment_characteristic> assignment_characteristic_list;
typedef std::vector<std::vector<assignment_cut>> assignment_cut_list;

environment parse_environment(const nlohmann::json& json);
task_map parse_tasks(const nlohmann::json& json);
assignment_characteristic_list parse_assignment_characteristics(const nlohmann::json& json);
solution parse_solution(const nlohmann::json& json);
assignment_cut_list parse_assignment_cuts(const nlohmann::json& json);

void write_tasks(nlohmann::json& json, const std::vector<task>& tasks);
void write_solution(nlohmann::json& json, const solution& solution);
void add_assignment_cuts(nlohmann::json& json, const std::vector<assignment_cut>& assignments);

bool read_json_from_file(nlohmann::json& json, const std::string& filename);
bool write_json_to_file(const nlohmann::json& json, const std::string& filename);

#endif // INSTANCE_H
