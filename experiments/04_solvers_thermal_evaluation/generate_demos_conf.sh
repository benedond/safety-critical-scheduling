#!/bin/bash

python ../generate_demos_config.py -i "imx8a/all" -f "solutions"
python ../generate_demos_config.py -i "imx8a/cpu" -f "solutions"
python ../generate_demos_config.py -i "imx8b/all" -f "solutions"
python ../generate_demos_config.py -i "imx8b/cpu" -f "solutions"
python ../generate_demos_config.py -i "tx2/all" -f "solutions"
python ../generate_demos_config.py -i "tx2/cpu" -f "solutions"