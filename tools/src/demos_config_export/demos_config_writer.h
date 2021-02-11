#ifndef DEMOS_CONFIG_WRITER_H
#define DEMOS_CONFIG_WRITER_H

#include <sstream>
#include <string>

#include "../common/instance.h"

class demos_config_writer
{
public:
	demos_config_writer(const environment& e, const task_map& t, const solution& s);

	std::string get_config();

private:
	const environment& m_environment;
	const task_map& m_tasks;
	const solution& m_solution;

	std::stringstream m_output;
	std::unordered_map<std::string, int> m_cpu_offset;
	bool m_config_exported;

	void write_config();
	void write_partition(const task& task);
	void write_window(const window& window);
	void write_empty_window(int length);
};

#endif // DEMOS_CONFIG_WRITER_H
