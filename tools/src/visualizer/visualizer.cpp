#include <iostream>
#include <cstdint>
#include <lodepng.h>

#include "visualizer.h"

#define Y_OFFSET 30U
#define X_OFFSET 20U

#define LANE_X_START (60U + X_OFFSET)
#define LANE_HEIGHT 30U
#define LANE_Y_OFFSET 5U
#define LANE_X_OFFSET 1U

#define TIME_SCALE 2

#define LINE_DASHED 0xF00FF00F

using namespace cimg_library;

const visualizer::uchar WHITE[] = { 0xFF, 0xFF, 0xFF };
const visualizer::uchar BLACK[] = { 0x00, 0x00, 0x00 };
const visualizer::uchar RED[] = { 0xFF, 0x00, 0x00 };
//constexpr visualizer::uchar BLUE[] = { 0x00, 0x00, 0xFF };
//constexpr visualizer::uchar CYAN[] = { 0x00, 0x80, 0x80 };
const visualizer::uchar LIGHT_VIOLET[] = { 0x96, 0x96, 0xFA };

visualizer::visualizer(const environment& e, const solution& s) :
		m_environment(e), m_solution(s), m_img_width(0), m_img_height(0), m_img_built(false)
{
	if (m_supported_problem_versions.find(e.problem_version) == m_supported_problem_versions.end())
		throw std::invalid_argument("problem version is not supported");
}

void visualizer::display()
{
#if (cimg_display == 0)
	std::cerr << "display is not supported, please recompile with display support" << std::endl;
#else
	build_image();

	CImgDisplay disp(m_img, "visualizer");
	while (!disp.is_closed())
		disp.wait();
#endif

}

void visualizer::export_bmp(const std::string& filename)
{
	build_image();
	m_img.save_bmp(filename.c_str());
}

void visualizer::export_png(const std::string& filename)
{
	build_image();

	const uint64_t img_buffer_size = m_img_width * m_img_height * 3;
	std::vector<uchar> buffer(img_buffer_size);

	for (uint64_t i=0; i<img_buffer_size; i+=3)
	{
		const uint64_t x = (i/3) % m_img_width;
		const uint64_t y = (i/3) / m_img_width;

		buffer[i+0] = m_img.atXYZC(x, y, 1, 0);
		buffer[i+1] = m_img.atXYZC(x, y, 1, 1);
		buffer[i+2] = m_img.atXYZC(x, y, 1, 2);
	}

	lodepng_encode24_file(filename.c_str(), buffer.begin().base(), m_img_width, m_img_height);
}

void visualizer::build_image()
{
	if (m_img_built)
		return;
	m_img_built = true;

	init_img();

	if (m_solution.feasible)
	{
		draw_grid();

		uint last_window_start = 0;
		for (auto& window : m_solution.windows)
			last_window_start = draw_window(window, last_window_start);
	}
	else
	{
		draw_infeasible_solution();
	}
}

void visualizer::init_img()
{
	for (auto& p : m_environment.processors_list)
		for (int i=0; i<p->processing_units; i++)
			m_processing_units.push_back(p->name);

	m_img_width = m_environment.major_frame_length * TIME_SCALE + 2 * X_OFFSET + LANE_X_START;
	m_img_height = m_processing_units.size() * LANE_HEIGHT + 2 * Y_OFFSET;
	m_img = img_type(m_img_width, m_img_height, 1, 3);
	m_img.draw_rectangle(0, 0, m_img_width, m_img_height, WHITE);
}

void visualizer::draw_grid()
{
	const uint min_x = X_OFFSET;
	const uint max_x = LANE_X_START + m_environment.major_frame_length*TIME_SCALE;
	uint y_pos = Y_OFFSET;

	// horizontalni cary
	std::string last_pu;
	for (auto& pu : m_processing_units)
	{
		if (pu != last_pu)
		{
			m_pu_offsets[pu] = y_pos;
			last_pu = pu;
		}

		m_img.draw_line(min_x, y_pos, max_x, y_pos, BLACK);
		m_img.draw_text(min_x + 10, (uint) (y_pos + 5), pu.c_str(), BLACK, WHITE);
		y_pos += LANE_HEIGHT;
	}
	m_img.draw_line(min_x, y_pos, max_x, y_pos, BLACK);

	// vertikalni cary
	const uint min_y = Y_OFFSET;
	const uint max_y = m_img_height - Y_OFFSET;
	const uint end_x = LANE_X_START + m_environment.major_frame_length * TIME_SCALE;
	//m_img.draw_line(LANE_X_START-1, min_y, LANE_X_START-1, max_y, BLACK);
	m_img.draw_line(LANE_X_START, min_y, LANE_X_START, max_y, BLACK);
	m_img.draw_line(end_x, min_y, end_x, max_y, BLACK);
	m_img.draw_line(end_x+1, min_y, end_x+1, max_y, BLACK);

	std::string mf_label = "MF: " + std::to_string(m_environment.major_frame_length) + "ms";
	m_img.draw_text((uint) (end_x - 25), (uint) (Y_OFFSET - 15), mf_label.c_str(), BLACK, WHITE);
}

visualizer::uint visualizer::draw_window(const window& window, uint window_start_time)
{
	const uint min_y = Y_OFFSET;
	const uint max_y = m_img_height - Y_OFFSET;

	uint window_start_x = LANE_X_START + window_start_time*TIME_SCALE;
	std::unordered_map<std::string, int> pu_allocations;

	for (auto& task_assignment : window.task_assignments)
	{
		uint start_x = window_start_x + task_assignment.start*TIME_SCALE;
		uint end_x = start_x + task_assignment.length*TIME_SCALE;

		uint start_y = m_pu_offsets.at(task_assignment.processor) + task_assignment.processing_unit * LANE_HEIGHT + LANE_Y_OFFSET;
		uint end_y = start_y + LANE_HEIGHT - LANE_Y_OFFSET*2;
		m_img.draw_rectangle((uint) (start_x + LANE_X_OFFSET), start_y, end_x, end_y, LIGHT_VIOLET);

		std::string label = task_assignment.task + ": " + std::to_string(task_assignment.length) + "ms";
		m_img.draw_text((uint) (start_x + 10), (uint) (start_y + 3), label.c_str(), BLACK);
	}

	uint end_x = window_start_x + window.length*TIME_SCALE;
	m_img.draw_line(end_x, min_y, end_x, max_y, RED, 1, LINE_DASHED);

	uint window_end = window_start_time + window.length;
	std::string window_label = std::to_string(window_end) + "ms";
	m_img.draw_text(end_x, (uint) (max_y + 1), window_label.c_str(), RED, WHITE);

	return window_end;
}

void visualizer::draw_infeasible_solution()
{
	m_img.draw_text(X_OFFSET, Y_OFFSET, "SOLUTION INFEASIBLE", RED, WHITE, 1, 18);
}