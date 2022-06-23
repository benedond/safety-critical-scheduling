#!/bin/bash

python ../generate_demos_config.py -i "500/tx2"
python ../generate_demos_config.py -i "500/imx8a"
python ../generate_demos_config.py -i "1000/tx2"

python ../generate_demos_config.py -i "500/imx8b"
python ../generate_demos_config.py -i "1000/imx8b"
