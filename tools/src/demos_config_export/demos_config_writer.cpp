#include <iostream>

#include "demos_config_writer.h"

#define YAML_INDENT "  "
#define YAML_NEWLINE "\n"

demos_config_writer::demos_config_writer(const environment& e, const task_map& t, const solution& s)
	: m_environment(e), m_tasks(t), m_solution(s), m_output(), m_cpu_offset(), m_config_exported(false)
{
}

std::string demos_config_writer::get_config()
{
	write_config();
	return m_output.str();
}

void demos_config_writer::write_config()
{
	if (m_config_exported)
		return;
	m_config_exported = true;

	if (!m_solution.feasible)
	{
		std::cerr << "error: solution is infeasible, nothing to export" << std::endl;
		return;
	}

	int current_cpu_offset = 0;
	for (auto& p : m_environment.processors_list)
	{
		m_cpu_offset[p->name] = current_cpu_offset;
		current_cpu_offset += p->processing_units;
	}

	m_output << "partitions:" << YAML_NEWLINE;
	for (auto& t : m_tasks)
		write_partition(t.second);

	m_output << YAML_NEWLINE;
	m_output << "windows:" << YAML_NEWLINE;

	int schedule_length = 0;
	for (auto& w : m_solution.windows)
	{
		write_window(w);
		schedule_length += w.length;
	}

	write_empty_window(m_environment.major_frame_length - schedule_length);
}

void demos_config_writer::write_partition(const task& task)
{
	m_output << YAML_INDENT << "- name: " << task.name << YAML_NEWLINE;
	m_output << YAML_INDENT << YAML_INDENT << "processes:" << YAML_NEWLINE;
	m_output << YAML_INDENT << YAML_INDENT << YAML_INDENT << "- cmd: " << task.command << YAML_NEWLINE;
	m_output << YAML_INDENT << YAML_INDENT << YAML_INDENT << YAML_INDENT << "budget: " << task.length << YAML_NEWLINE;
}

void demos_config_writer::write_window(const window& window)
{
	std::unordered_map<std::string, std::vector<int>> cpu_mappings;

	for (auto& t : window.task_assignments)
	{
		if (m_environment.processors.at(t.processor).type == processor_type::main_processor)
			cpu_mappings[t.task].push_back(m_cpu_offset[t.processor] + t.processing_unit);
	}

	m_output << YAML_INDENT << "- length: " << window.length << YAML_NEWLINE;
	m_output << YAML_INDENT << YAML_INDENT << "slices:" << YAML_NEWLINE;

	for (auto& t : cpu_mappings)
	{
		m_output << YAML_INDENT << YAML_INDENT << YAML_INDENT << "- cpu: ";

		for (int cpu : t.second)
			m_output << cpu << ",";
		m_output.seekp(-1, std::stringstream::cur);
		m_output << YAML_NEWLINE;

		m_output << YAML_INDENT << YAML_INDENT << YAML_INDENT << YAML_INDENT << "sc_partition: " << t.first << YAML_NEWLINE;
	}
}

void demos_config_writer::write_empty_window(int length)
{
	if (length < 1)
		return;

	m_output << YAML_INDENT << "- length: " << length << YAML_NEWLINE;
	m_output << YAML_INDENT << YAML_INDENT << "slices:" << YAML_NEWLINE;
	m_output << YAML_INDENT << YAML_INDENT << YAML_INDENT << "- cpu: 0" << YAML_NEWLINE;
}