#!/bin/bash

# Benchmark characteristis
python generate_results.py  -e ../../data/environment-imx8b.json -o "./results/characteristics-imx8b-all.csv" -m "./measurements/imx8b" -b "../../data/benchmarks.csv"

# Power file by file
python ../get_results.py instances/imx8b/ results/imx8b.csv  # compute base characteristics
python3 ../add_measured_data.py -r ./results/imx8b.csv -m ./measurements/imx8b/ -c power  # add power
