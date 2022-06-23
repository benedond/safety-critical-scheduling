#!/bin/bash

# window 500+500
python generate_instances.py --window_length 500 --env_file ../../data/environment-tx2.json --char_file ../../data/characteristics-tx2-all.csv --out_folder instances/500/tx2 --n_instances 4 --experiment_type single
python generate_instances.py --window_length 500 --env_file ../../data/environment-tx2.json --char_file ../../data/characteristics-tx2-all.csv --out_folder instances/500/tx2 --n_instances 4 --experiment_type all

python generate_instances.py --window_length 500 --env_file ../../data/environment-imx8a.json --char_file ../../data/characteristics-imx8a-all.csv --out_folder instances/500/imx8a --n_instances 4 --experiment_type single
python generate_instances.py --window_length 500 --env_file ../../data/environment-imx8a.json --char_file ../../data/characteristics-imx8a-all.csv --out_folder instances/500/imx8a --n_instances 4 --experiment_type all

python generate_instances.py --window_length 500 --env_file ../../data/environment-imx8b.json --char_file ../../data/characteristics-imx8b-all.csv --out_folder instances/500/imx8b --n_instances 4 --experiment_type single
python generate_instances.py --window_length 500 --env_file ../../data/environment-imx8b.json --char_file ../../data/characteristics-imx8b-all.csv --out_folder instances/500/imx8b --n_instances 4 --experiment_type all




# window 1000+1000
python generate_instances.py --window_length 1000 --env_file ../../data/environment-tx2.json --char_file ../../data/characteristics-tx2-all.csv --out_folder instances/1000/tx2 --n_instances 4 --experiment_type single
python generate_instances.py --window_length 1000 --env_file ../../data/environment-tx2.json --char_file ../../data/characteristics-tx2-all.csv --out_folder instances/1000/tx2 --n_instances 4 --experiment_type all

python generate_instances.py --window_length 1000 --env_file ../../data/environment-imx8b.json --char_file ../../data/characteristics-imx8b-all.csv --out_folder instances/1000/imx8b --n_instances 4 --experiment_type single
python generate_instances.py --window_length 1000 --env_file ../../data/environment-imx8b.json --char_file ../../data/characteristics-imx8b-all.csv --out_folder instances/1000/imx8b --n_instances 4 --experiment_type all
