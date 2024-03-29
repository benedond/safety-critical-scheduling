#ifndef VISUALIZER_H
#define VISUALIZER_H

#include <CImg.h>
#include <unordered_set>

#include "../common/instance.h"

class visualizer
{
public:
	typedef unsigned int uint;
	typedef unsigned char uchar;
	typedef cimg_library::CImg<uchar> img_type;

	void display();
	void export_bmp(const std::string& filename);
	void export_png(const std::string& filename);

	visualizer(const environment& e, const solution& s);

private:
	const std::unordered_set<int> m_supported_problem_versions { 1, 2 };

	const environment& m_environment;
	const solution& m_solution;

	std::unordered_map<std::string, uint> m_pu_offsets;
	std::vector<std::string> m_processing_units;
	uint m_img_width, m_img_height;
	img_type m_img;
	bool m_img_built;

	void init_img();
	void draw_grid();
	uint draw_window(const window& window, uint window_start_time);
	void draw_infeasible_solution();
	void build_image();
};

#endif // VISUALIZER_H
