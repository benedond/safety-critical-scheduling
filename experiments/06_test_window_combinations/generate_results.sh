#!/bin/bash

# Compute the results based on the pre-generated instances (solutions)
python ../get_results.py -i instances/500/tx2 -o results/500-tx2.csv -l ../../data/LR-coefficients.json -p tx2
python ../get_results.py -i instances/1000/tx2 -o results/1000-tx2.csv -l ../../data/LR-coefficients.json -p tx2


# Add power measurements to the solutions
python3 ../add_measured_data.py -r ./results/500-tx2.csv -m ./measurements/500/tx2/ -c power -e ../../data/environment-tx2.json
python3 ../add_measured_data.py -r ./results/1000-tx2.csv -m ./measurements/1000/tx2/ -c power -e ../../data/environment-tx2.json

