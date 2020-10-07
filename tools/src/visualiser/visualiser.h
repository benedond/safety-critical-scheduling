#ifndef _VISUALISER_H
#define _VISUALISER_H

#include <CImg.h>

#include "../common/instance.h"

class visualiser
{
public:
	typedef unsigned int uint;
	typedef unsigned char uchar;
	typedef cimg_library::CImg<uchar> img_type;

	void display();
	void export_bmp(const std::string& filename);

	visualiser(const Environment& e, const std::unordered_map<std::string, Task>& t, const Solution& s);

private:
	const Environment& m_environment;
	const std::unordered_map<std::string, Task>& m_tasks;
	const Solution& m_solution;

	std::unordered_map<std::string, uint> m_pu_offsets;
	std::vector<std::string> m_processing_units;
	uint m_img_width, m_img_height;
	img_type m_img;
	bool m_img_built;

	void init_img();
	void draw_grid();
	uint draw_window(const Window& window, uint window_start_time);
	void draw_infeasible_solution();
	void build_image();
};

#endif // _VISUALISER_H
