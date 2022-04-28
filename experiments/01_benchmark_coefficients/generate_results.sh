#!/bin/bash

# Benchmark characteristis
python generate_results.py  -e ../../data/environment-imx8b.json -o "./results/characteristics-imx8b-all.csv" -m "./measurements/imx8b" -b "../../data/benchmarks.csv"
python generate_results.py  -e ../../data/environment-tx2.json -o "./results/characteristics-tx2-all.csv" -m "./measurements/tx2" -b "../../data/benchmarks.csv"

# Power file by file
python ../get_results.py -i instances/imx8b/ -o results/imx8b.csv -l ../../data/LR-coefficients.json -p imx8b # compute base characteristics
python ../get_results.py -i instances/tx2/   -o results/tx2.csv   -l ../../data/LR-coefficients.json -p tx2   # compute base characteristics

python3 ../add_measured_data.py -r ./results/imx8b.csv -m ./measurements/imx8b/ -c power  # add power
python3 ../add_measured_data.py -r ./results/tx2.csv -m ./measurements/tx2/ -c power  # add power
