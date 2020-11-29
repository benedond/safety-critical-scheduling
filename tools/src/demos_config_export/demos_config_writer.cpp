#include <iostream>

#include "demos_config_writer.h"

#define YAML_INDENT "  "
#define YAML_NEWLINE "\n"

demos_config_writer::demos_config_writer(const environment& e, const task_map& t, const solution& s)
	: env(e), tasks(t), sol(s), output(), cpu_offset(), config_exported(false)
{
}

std::string demos_config_writer::get_config()
{
	write_config();
	return output.str();
}

void demos_config_writer::write_config()
{
	if (config_exported)
		return;
	config_exported = true;

	if (!sol.feasible)
	{
		std::cerr << "error: solution is infeasible, nothing to export" << std::endl;
		return;
	}

	int current_cpu_offset = 0;
	for (auto& p : env.processors_list)
	{
		cpu_offset[p->name] = current_cpu_offset;
		current_cpu_offset += p->processing_units;
	}

	output << "partitions:" << YAML_NEWLINE;
	for (auto& t : tasks)
		write_partition(t.second);

	output << YAML_NEWLINE;
	output << "windows:" << YAML_NEWLINE;

	for (auto& w : sol.windows)
		write_window(w);
}

void demos_config_writer::write_partition(const task& task)
{
	output << YAML_INDENT << "- name: " << task.name << YAML_NEWLINE;
	output << YAML_INDENT << YAML_INDENT << "processes:" << YAML_NEWLINE;
	output << YAML_INDENT << YAML_INDENT << YAML_INDENT << "- cmd: " << task.command << YAML_NEWLINE;
	output << YAML_INDENT << YAML_INDENT << YAML_INDENT << YAML_INDENT << "budget: " << task.length << YAML_NEWLINE;
}

void demos_config_writer::write_window(const window& window)
{
	output << YAML_INDENT << "- length: " << window.length << YAML_NEWLINE;
	output << YAML_INDENT << YAML_INDENT << "slices:" << YAML_NEWLINE;

	for (auto& t : window.task_assignments)
	{
		output << YAML_INDENT << YAML_INDENT << YAML_INDENT << "- cpu: " << cpu_offset[t.processor] + t.processing_unit << YAML_NEWLINE;
		output << YAML_INDENT << YAML_INDENT << YAML_INDENT << YAML_INDENT << "sc_partition: " << t.task << YAML_NEWLINE;
	}
}