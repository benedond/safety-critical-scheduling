#!/bin/bash

# Benchmark characteristis
python generate_results.py  -e ../../data/environment-imx8a.json -o "./results/characteristics-imx8a-all.csv" -m "./measurements/imx8a" -b "../../data/benchmarks.csv"
python generate_results.py  -e ../../data/environment-imx8b.json -o "./results/characteristics-imx8b-all.csv" -m "./measurements/imx8b" -b "../../data/benchmarks.csv"
python generate_results.py  -e ../../data/environment-tx2.json -o "./results/characteristics-tx2-all_old.csv" -m "./measurements/tx2" -b "../../data/benchmarks.csv"
python generate_results.py  -e ../../data/environment-tx2.json -o "./results/characteristics-tx2-all.csv" -m "./measurements_repeated/tx2" -b "../../data/benchmarks.csv"

python generate_results.py  -e ../../data/environment-imx8a.json -o "./results/characteristics-imx8a-cpu.csv" -m "./measurements/imx8a" -b "../../data/benchmarks.csv" -c 1
python generate_results.py  -e ../../data/environment-imx8b.json -o "./results/characteristics-imx8b-cpu.csv" -m "./measurements/imx8b" -b "../../data/benchmarks.csv" -c 1
python generate_results.py  -e ../../data/environment-tx2.json -o "./results/characteristics-tx2-cpu_old.csv" -m "./measurements/tx2" -b "../../data/benchmarks.csv" -c 1
python generate_results.py  -e ../../data/environment-tx2.json -o "./results/characteristics-tx2-cpu.csv" -m "./measurements_repeated/tx2" -b "../../data/benchmarks.csv" -c 1

# Power file by file
# - compute base characteristics
python ../get_results.py -i instances/imx8a/ -o results/imx8a.csv -l ../../data/LR-coefficients.json -p imx8a 
python ../get_results.py -i instances/imx8b/ -o results/imx8b.csv -l ../../data/LR-coefficients.json -p imx8b
python ../get_results.py -i instances/tx2/   -o results/tx2_old.csv   -l ../../data/LR-coefficients.json -p tx2
python ../get_results.py -i instances/tx2/   -o results/tx2.csv   -l ../../data/LR-coefficients.json -p tx2
# - add power
python3 ../add_measured_data.py -r ./results/imx8a.csv -m ./measurements/imx8a/ -c power -e ../../data/environment-imx8a.json
python3 ../add_measured_data.py -r ./results/imx8b.csv -m ./measurements/imx8b/ -c power -e ../../data/environment-imx8b.json
python3 ../add_measured_data.py -r ./results/tx2_old.csv -m ./measurements/tx2/ -c power -e ../../data/environment-tx2.json
python3 ../add_measured_data.py -r ./results/tx2.csv -m ./measurements_repeated/tx2/ -c power -e ../../data/environment-tx2.json
