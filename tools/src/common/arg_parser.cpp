#include "arg_parser.h"

arg_parser::arg_parser(int argc, char** argv)
{
	m_args.reserve(argc);

	for (int i=0; i<argc; i++)
	{
		m_args.emplace_back(argv[i]);
		m_arg_pos.emplace(argv[i], i);
	}
}

bool arg_parser::is_arg_present(const std::string& arg) const
{
	return m_arg_pos.find(arg) != m_arg_pos.end();
}

std::string arg_parser::get_arg_value(const std::string& arg) const
{
	 auto m_arg_pos_itt = m_arg_pos.find(arg);

	 // argument not found
	 if (m_arg_pos_itt == m_arg_pos.end())
	 	return "";

	 // argument has no value
	 int val_pos = m_arg_pos_itt->second+1;
	 if (val_pos >= m_args.size())
	 	return "";

	 return m_args[val_pos];
}

void arg_parser::set_arg_value_int(const std::string& arg, int* val) const
{
	std::string arg_val = get_arg_value(arg);

	if (!arg_val.empty())
		*val = std::stoi(arg_val);
}
