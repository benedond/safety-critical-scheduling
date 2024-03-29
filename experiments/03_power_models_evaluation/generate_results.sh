#!/bin/bash

# Compute the results based on the pre-generated instances (solutions)
python ../get_results.py -i instances/scale-1x/imx8a/all/ -o results/scale-1x-imx8a-all.csv -l ../../data/LR-coefficients.json -p imx8a
python ../get_results.py -i instances/scale-1x/imx8a/cpu/ -o results/scale-1x-imx8a-cpu.csv -l ../../data/LR-coefficients.json -p imx8a
python ../get_results.py -i instances/scale-1x/imx8b/all/ -o results/scale-1x-imx8b-all.csv -l ../../data/LR-coefficients.json -p imx8b
python ../get_results.py -i instances/scale-1x/imx8b/cpu/ -o results/scale-1x-imx8b-cpu.csv -l ../../data/LR-coefficients.json -p imx8b
python ../get_results.py -i instances/scale-1x/tx2/all/ -o results/scale-1x-tx2-all.csv -l ../../data/LR-coefficients.json -p tx2
python ../get_results.py -i instances/scale-1x/tx2/cpu/ -o results/scale-1x-tx2-cpu.csv -l ../../data/LR-coefficients.json -p tx2

# Add power measurements to the solutions
python3 ../add_measured_data.py -r ./results/scale-1x-imx8a-all.csv -m ./measurements/scale-1x/imx8a/all/ -c power -e ../../data/environment-imx8a.json
python3 ../add_measured_data.py -r ./results/scale-1x-imx8a-cpu.csv -m ./measurements/scale-1x/imx8a/cpu/ -c power -e ../../data/environment-imx8a.json
python3 ../add_measured_data.py -r ./results/scale-1x-imx8b-all.csv -m ./measurements/scale-1x/imx8b/all/ -c power -e ../../data/environment-imx8b.json
python3 ../add_measured_data.py -r ./results/scale-1x-imx8b-cpu.csv -m ./measurements/scale-1x/imx8b/cpu/ -c power -e ../../data/environment-imx8b.json
python3 ../add_measured_data.py -r ./results/scale-1x-tx2-all.csv -m ./measurements/scale-1x/tx2/all/ -c power -e ../../data/environment-tx2.json
python3 ../add_measured_data.py -r ./results/scale-1x-tx2-cpu.csv -m ./measurements/scale-1x/tx2/cpu/ -c power -e ../../data/environment-tx2.json
