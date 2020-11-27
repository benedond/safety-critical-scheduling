#include <fstream>
#include <string>

#include "ilp_util.h"

void write_iis(const std::string& filename, GRBModel& model)
{
    std::string infeasible_filename(filename + ".ilp");

    for (int i = 1; i < 1000; i++)
    {
        std::ifstream file(infeasible_filename);
        if (file.is_open())
        {
            infeasible_filename = filename + "-" + std::to_string(i) + ".ilp";
        }
        else
        {
            file.close();
            model.write(infeasible_filename);
            return;
        }
    }
}