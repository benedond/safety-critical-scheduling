#!/bin/bash

# Compute the results based on the pre-generated instances (solutions)
python ../get_results.py instances/scale-1x/imx8a/all/ results/scale-1x-imx8a-all.csv
python ../get_results.py instances/scale-1x/imx8a/cpu/ results/scale-1x-imx8a-cpu.csv
python ../get_results.py instances/scale-1x/imx8b/all/ results/scale-1x-imx8b-all.csv
python ../get_results.py instances/scale-1x/imx8b/cpu/ results/scale-1x-imx8b-cpu.csv

python ../get_results.py instances/scale-3x/imx8a/all/ results/scale-3x-imx8a-all.csv
python ../get_results.py instances/scale-3x/imx8a/cpu/ results/scale-3x-imx8a-cpu.csv
python ../get_results.py instances/scale-3x/imx8b/all/ results/scale-3x-imx8b-all.csv
python ../get_results.py instances/scale-3x/imx8b/cpu/ results/scale-3x-imx8b-cpu.csv

# Add power measurements to the solutions
python3 ../add_measured_data.py -r ./results/scale-1x-imx8a-all.csv -m ./measurements/scale-1x/imx8a/all/ -c power
python3 ../add_measured_data.py -r ./results/scale-1x-imx8a-cpu.csv -m ./measurements/scale-1x/imx8a/cpu/ -c power
python3 ../add_measured_data.py -r ./results/scale-1x-imx8b-all.csv -m ./measurements/scale-1x/imx8b/all/ -c power
python3 ../add_measured_data.py -r ./results/scale-1x-imx8b-cpu.csv -m ./measurements/scale-1x/imx8b/cpu/ -c power

python3 ../add_measured_data.py -r ./results/scale-3x-imx8a-all.csv -m ./measurements/scale-3x/imx8a/all/ -c power
python3 ../add_measured_data.py -r ./results/scale-3x-imx8a-cpu.csv -m ./measurements/scale-3x/imx8a/cpu/ -c power
python3 ../add_measured_data.py -r ./results/scale-3x-imx8b-all.csv -m ./measurements/scale-3x/imx8b/all/ -c power
python3 ../add_measured_data.py -r ./results/scale-3x-imx8b-cpu.csv -m ./measurements/scale-3x/imx8b/cpu/ -c power


# 30-s experiment at imx8-b
python ../get_results.py instances/scale-1x/imx8b/all/ results/scale-1x-imx8b-all-30.csv
python ../get_results.py instances/scale-1x/imx8b/cpu/ results/scale-1x-imx8b-cpu-30.csv
python3 ../add_measured_data.py -r ./results/scale-1x-imx8b-all-30.csv -m ./measurements/scale-1x/imx8b/all-30/ -c power
python3 ../add_measured_data.py -r ./results/scale-1x-imx8b-cpu-30.csv -m ./measurements/scale-1x/imx8b/cpu-30/ -c power