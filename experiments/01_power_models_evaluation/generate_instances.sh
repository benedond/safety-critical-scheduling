#!/bin/bash

# scale - 1x
python generate_instances.py --window_length 1000 --env_file ../../data/environment-imx8.json --char_file ../../data/characteristics-imx8a-all.csv --out_folder instances/scale-1x/imx8a/all

python generate_instances.py --window_length 1000 --env_file ../../data/environment-imx8.json --char_file ../../data/characteristics-imx8a-cpu.csv --out_folder instances/scale-1x/imx8a/cpu

python generate_instances.py --window_length 1000 --env_file ../../data/environment-imx8.json --char_file ../../data/characteristics-imx8b-all.csv --out_folder instances/scale-1x/imx8b/all

python generate_instances.py --window_length 1000 --env_file ../../data/environment-imx8.json --char_file ../../data/characteristics-imx8b-cpu.csv --out_folder instances/scale-1x/imx8b/cpu

# scale - 3x
python generate_instances.py --window_length 1000 --scale 3 --env_file ../../data/environment-imx8.json --char_file ../../data/characteristics-imx8a-all.csv --out_folder instances/scale-3x/imx8a-3x/all

python generate_instances.py --window_length 1000 --scale 3 --env_file ../../data/environment-imx8.json --char_file ../../data/characteristics-imx8a-cpu.csv --out_folder instances/scale-3x/imx8a-3x/cpu

python generate_instances.py --window_length 1000 --scale 3 --env_file ../../data/environment-imx8.json --char_file ../../data/characteristics-imx8b-all.csv --out_folder instances/scale-3x/imx8b-3x/all

python generate_instances.py --window_length 1000 --scale 3 --env_file ../../data/environment-imx8.json --char_file ../../data/characteristics-imx8b-cpu.csv --out_folder instances/scale-3x/imx8b-3x/cpu

