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
	const environment& env;
	const task_map& tasks;
	const solution& sol;

	std::stringstream output;
	std::unordered_map<std::string, int> cpu_offset;
	bool config_exported;

	void write_config();
	void write_partition(const task& task);
	void write_window(const window& window);
};

#endif // DEMOS_CONFIG_WRITER_H
