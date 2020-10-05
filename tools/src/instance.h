#ifndef _INSTANCE_H
#define _INSTANCE_H

#include <string>
#include <vector>
#include <unordered_map>
#include "lib/nlohmann/json.hpp"

struct Processor
{
	std::string name;
	int processing_units;
};

struct Environment
{
	std::unordered_map<std::string, Processor> processors;
	int main_frame_length;
};

struct Task
{
	std::string name;
	int length;
	std::vector<std::string> processors;
};

struct Window
{
	int length;
	std::vector<std::string> tasks;
};

struct Solution
{
	bool feasible;
	std::vector<Window> windows;
};

Environment parse_environment(const nlohmann::json& json);
std::unordered_map<std::string, Task> parse_tasks(const nlohmann::json& json);
Solution parse_solution(const nlohmann::json& json);

#endif // _INSTANCE_H
