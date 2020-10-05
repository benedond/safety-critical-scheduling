#include "visualiser.h"

#define Y_OFFSET 30U
#define X_OFFSET 20U

#define LANE_X_START (60U + X_OFFSET)
#define LANE_HEIGHT 30U
#define LANE_Y_OFFSET 5U
#define LANE_X_OFFSET 1U

#define TIME_SCALE 4

#define LINE_DASHED 0xF00FF00F

using namespace cimg_library;

constexpr Visualiser::uchar WHITE[] = { 0xFF, 0xFF, 0xFF };
constexpr Visualiser::uchar BLACK[] = { 0x00, 0x00, 0x00 };
constexpr Visualiser::uchar RED[] = { 0xFF, 0x00, 0x00 };
//constexpr Visualiser::uchar BLUE[] = { 0x00, 0x00, 0xFF };
constexpr Visualiser::uchar CYAN[] = { 0x00, 0x80, 0x80 };

Visualiser::Visualiser(const Environment& e, const std::unordered_map<std::string, Task>& t, const Solution& s) :
		environment(e), tasks(t), solution(s), img_built(false), img_width(0), img_height(0)
{
}

void Visualiser::display()
{
	build_image();

	CImgDisplay disp(img, "Visualiser");
	while (!disp.is_closed()) disp.wait();
}

void Visualiser::export_bmp(const std::string& filename)
{
	build_image();
	img.save_bmp(filename.c_str());
}

void Visualiser::build_image()
{
	if (img_built)
		return;

	init_img();

	if (solution.feasible)
	{
		draw_grid();

		uint last_window_start = 0;
		for (auto& window : solution.windows)
			last_window_start = draw_window(window, last_window_start);
	}
	else
	{
		draw_infeasible_solution();
	}

	img_built = true;
}

void Visualiser::init_img()
{
	for (auto& p : environment.processors)
	{
		for (int i=0; i<p.second.processing_units; i++)
		{
			processing_units.push_back(p.first);
		}
	}

	img_width = environment.main_frame_length * TIME_SCALE + 2*X_OFFSET + LANE_X_START;
	img_height = processing_units.size() * LANE_HEIGHT + 2*Y_OFFSET;
	img = img_type(img_width, img_height, 1, 4);
	img.draw_rectangle(0, 0, img_width, img_height, WHITE);
}

void Visualiser::draw_grid()
{
	const uint min_x = X_OFFSET;
	const uint max_x = img_width - X_OFFSET;
	uint y_pos = Y_OFFSET;

	// horizontalni cary
	std::string last_pu;
	for (auto& pu : processing_units)
	{
		if (pu != last_pu)
		{
			pu_offsets[pu] = y_pos;
			last_pu = pu;
		}

		img.draw_line(min_x, y_pos, max_x, y_pos, BLACK);
		img.draw_text(min_x + 10, (uint) (y_pos + 5), pu.c_str(), BLACK, WHITE);
		y_pos += LANE_HEIGHT;
	}
	img.draw_line(min_x, y_pos, max_x, y_pos, BLACK);

	// vertikalni cary
	const uint min_y = Y_OFFSET;
	const uint max_y = img_height - Y_OFFSET;
	const uint end_x = LANE_X_START + environment.main_frame_length*TIME_SCALE;
	img.draw_line(LANE_X_START, min_y, LANE_X_START, max_y, BLACK);
	img.draw_line(end_x, min_y, end_x, max_y, BLACK);

	std::string mf_label = "MF: " + std::to_string(environment.main_frame_length) + "ms";
	img.draw_text(end_x-20, max_y+1, mf_label.c_str(), BLACK, WHITE);
}

Visualiser::uint Visualiser::draw_window(const Window& window, uint window_start_time)
{
	const uint min_y = Y_OFFSET;
	const uint max_y = img_height - Y_OFFSET;

	uint start_x = LANE_X_START + window_start_time*TIME_SCALE;
	std::unordered_map<std::string, int> pu_allocations;

	for (auto& task : window.tasks)
	{
		auto& task_data = tasks.at(task);
		uint end_x = start_x + task_data.length*TIME_SCALE;

		for (auto& proc : task_data.processors)
		{
			int pu_allocation = pu_allocations[proc];
			pu_allocations[proc] = pu_allocation + 1;
			uint start_y = pu_offsets.at(proc) + pu_allocation*LANE_HEIGHT+LANE_Y_OFFSET;
			uint end_y = start_y + LANE_HEIGHT - LANE_Y_OFFSET*2;

			img.draw_rectangle((uint) (start_x + LANE_X_OFFSET), start_y, end_x, end_y, CYAN);

			std::string label = task + ": " + std::to_string(task_data.length) + "ms";
			img.draw_text((uint) (start_x + 10), (uint) (start_y + 3), label.c_str(), WHITE, CYAN);
		}
	}

	uint end_x = start_x + window.length*TIME_SCALE;
	img.draw_line(end_x, min_y, end_x, max_y, RED, 1, LINE_DASHED);

	uint window_end = window_start_time + window.length;
	std::string window_label = std::to_string(window_end) + "ms";
	img.draw_text(end_x, max_y+1, window_label.c_str(), RED, WHITE);

	return window_end;
}

void Visualiser::draw_infeasible_solution()
{
	img.draw_text(X_OFFSET, Y_OFFSET, "SOLUTION INFEASIBLE", RED, WHITE, 1, 18);
}