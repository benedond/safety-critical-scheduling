#ifndef _VISUALISER_H
#define _VISUALISER_H

#include "lib/CImg.h"
#include "instance.h"

class Visualiser
{
public:
	typedef unsigned int uint;
	typedef unsigned char uchar;
	typedef cimg_library::CImg<uchar> img_type;

	void display();
	void export_bmp(const std::string& filename);

	Visualiser(const Environment& e, const std::unordered_map<std::string, Task>& t, const Solution& s);

private:
	const Environment& environment;
	const std::unordered_map<std::string, Task>& tasks;
	const Solution& solution;

	std::unordered_map<std::string, uint> pu_offsets;
	std::vector<std::string> processing_units;
	uint img_width, img_height;
	img_type img;
	bool img_built;

	void init_img();
	void draw_grid();
	uint draw_window(const Window& window, uint window_start_time);
	void draw_infeasible_solution();
	void build_image();
};

#endif // _VISUALISER_H
