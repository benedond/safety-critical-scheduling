#ifndef ARG_PARSER_H
#define ARG_PARSER_H

#include <unordered_map>
#include <vector>
#include <string>

class arg_parser
{
public:
	bool is_arg_present(const std::string& arg) const;
	std::string get_arg_value(const std::string& arg) const;
	void set_arg_value_int(const std::string& arg, int* val) const;

	arg_parser(int argc, char** argv);

private:
	std::unordered_map<std::string, int> m_arg_pos;
	std::vector<std::string> m_args;
};

#endif // ARG_PARSER_H
