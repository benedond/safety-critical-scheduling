#include <iostream>
#include <fstream>

#include "instance.h"
#include "visualiser.h"

int main(int argc, char** argv)
{
	std::ifstream fs("../../../data/test_solution.json");

	if (!fs.is_open())
	{
		std::cerr << "failed to open file";
		return EXIT_FAILURE;
	}

	nlohmann::json json;
	fs >> json;

	auto e = parse_environment(json);
	auto t = parse_tasks(json);
	auto s = parse_solution(json);

	Visualiser v(e, t, s);
	v.display();

	return EXIT_SUCCESS;
}