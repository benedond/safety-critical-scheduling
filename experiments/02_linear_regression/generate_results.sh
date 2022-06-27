#!/bin/bash

# Power file by file ----------------------------------------------
# compute base characteristics
python ../get_results.py -i instances/imx8a/ -o results/imx8a.csv -l ../../data/LR-coefficients.json -p imx8a -s mapping.json 
python ../get_results.py -i instances/imx8b/ -o results/imx8b.csv -l ../../data/LR-coefficients.json -p imx8b -s mapping.json
python ../get_results.py -i instances/tx2/   -o results/tx2.csv   -l ../../data/LR-coefficients.json -p tx2 -s mapping.json   

# add power
python3 ../add_measured_data.py -r ./results/imx8a.csv -m ./measurements/imx8a/ -c power -e ../../data/environment-imx8a.json
python3 ../add_measured_data.py -r ./results/imx8b.csv -m ./measurements/imx8b/ -c power
python3 ../add_measured_data.py -r ./results/tx2.csv -m ./measurements/tx2/ -c power -e ../../data/environment-tx2.json

# LR coefficients --------------------------------------------------
python generate_results.py --c ../../data/characteristics-imx8a-all.csv -e ../../data/environment-imx8a.json -r ./results/imx8a.csv -o ./results/LR-coefficients.json -m ./instances/imx8a/mapping.json -p imx8a
python generate_results.py --c ../../data/characteristics-imx8b-all.csv -e ../../data/environment-imx8b.json -r ./results/imx8b.csv -o ./results/LR-coefficients.json -m ./instances/imx8b/mapping.json -p imx8b
python generate_results.py --c ../../data/characteristics-tx2-all.csv -e ../../data/environment-tx2.json -r ./results/tx2.csv -o ./results/LR-coefficients.json -m ./instances/tx2/mapping.json -p tx2 --tst_file ../01_benchmark_coefficients/results/tx2.csv
