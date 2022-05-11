#!/bin/bash

# scale - 1x
python generate_instances.py --window_length 1000 --env_file ../../data/environment-imx8a.json --char_file ../../data/characteristics-imx8a-all.csv --out_folder instances/scale-1x/imx8a/all
python generate_instances.py --window_length 1000 --env_file ../../data/environment-imx8a.json --char_file ../../data/characteristics-imx8a-cpu.csv --out_folder instances/scale-1x/imx8a/cpu
python generate_instances.py --window_length 1000 --env_file ../../data/environment-imx8b.json --char_file ../../data/characteristics-imx8b-all.csv --out_folder instances/scale-1x/imx8b/all
python generate_instances.py --window_length 1000 --env_file ../../data/environment-imx8b.json --char_file ../../data/characteristics-imx8b-cpu.csv --out_folder instances/scale-1x/imx8b/cpu
python generate_instances.py --window_length 1000 --env_file ../../data/environment-tx2.json --char_file ../../data/characteristics-tx2-all.csv --out_folder instances/scale-1x/tx2/all
python generate_instances.py --window_length 1000 --env_file ../../data/environment-tx2.json --char_file ../../data/characteristics-tx2-cpu.csv --out_folder instances/scale-1x/tx2/cpu


# scale - 3x
# python generate_instances.py --window_length 1000 --scale 3 --env_file ../../data/environment-imx8a.json --char_file ../../data/characteristics-imx8a-all.csv --out_folder instances/scale-3x/imx8a/all
# python generate_instances.py --window_length 1000 --scale 3 --env_file ../../data/environment-imx8a.json --char_file ../../data/characteristics-imx8a-cpu.csv --out_folder instances/scale-3x/imx8a/cpu
# python generate_instances.py --window_length 1000 --scale 3 --env_file ../../data/environment-imx8b.json --char_file ../../data/characteristics-imx8b-all.csv --out_folder instances/scale-3x/imx8b/all
# python generate_instances.py --window_length 1000 --scale 3 --env_file ../../data/environment-imx8b.json --char_file ../../data/characteristics-imx8b-cpu.csv --out_folder instances/scale-3x/imx8b/cpu

# scale - 10x
#python generate_instances.py --window_length 1000 --scale 10 --env_file ../../data/environment-imx8b.json --char_file ../../data/characteristics-imx8b-all.csv --out_folder instances/scale-10x/imx8b/all
#python generate_instances.py --window_length 1000 --scale 10 --env_file ../../data/environment-imx8b.json --char_file ../../data/characteristics-imx8b-cpu.csv --out_folder instances/scale-10x/imx8b/cpu
