#!/bin/bash

python generate_instances.py -e ../../data/environment-imx8a.json -b ../../data/benchmarks.csv -o instances/imx8a/ -c ../../data/characteristics-imx8a-all.csv -n 1000
python generate_instances.py -e ../../data/environment-imx8b.json -b ../../data/benchmarks.csv -o instances/imx8b/ -c ../../data/characteristics-imx8b-all.csv -n 1000
python generate_instances.py -e ../../data/environment-tx2.json -b ../../data/benchmarks.csv -o instances/tx2/ -c ../../data/characteristics-tx2-all.csv -n 1000