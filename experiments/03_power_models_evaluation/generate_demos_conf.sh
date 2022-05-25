#!/bin/bash

python ../generate_demos_config.py -i "scale-1x/imx8a/all"
python ../generate_demos_config.py -i "scale-1x/imx8a/cpu"
python ../generate_demos_config.py -i "scale-1x/imx8b/all"
python ../generate_demos_config.py -i "scale-1x/imx8b/cpu"
python ../generate_demos_config.py -i "scale-1x/tx2/all"
python ../generate_demos_config.py -i "scale-1x/tx2/cpu"