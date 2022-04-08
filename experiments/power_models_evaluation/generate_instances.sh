#!/bin/bash

python generate_instances.py --window_length 1000 --env_file ../../data/environment-imx8.json --char_file ../../data/characteristics-imx8a-all.csv --out_folder instances/imx8a/all

python generate_instances.py --window_length 1000 --env_file ../../data/environment-imx8.json --char_file ../../data/characteristics-imx8a-cpu.csv --out_folder instances/imx8a/cpu
