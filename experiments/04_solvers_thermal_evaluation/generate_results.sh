#!/bin/bash

# Compute the results based on the pre-generated instances (solutions)
python ../get_results.py -i solutions/imx8a/all/ -o results/imx8a-all.csv -l ../../data/LR-coefficients.json -p imx8a --include_only .json
python ../get_results.py -i solutions/imx8a/cpu/ -o results/imx8a-cpu.csv -l ../../data/LR-coefficients.json -p imx8a --include_only .json
python ../get_results.py -i solutions/imx8b/all/ -o results/imx8b-all.csv -l ../../data/LR-coefficients.json -p imx8b --include_only .json
python ../get_results.py -i solutions/imx8b/cpu/ -o results/imx8b-cpu.csv -l ../../data/LR-coefficients.json -p imx8b --include_only .json
python ../get_results.py -i solutions/tx2/all/   -o results/tx2-all.csv   -l ../../data/LR-coefficients.json -p tx2 --include_only .json
python ../get_results.py -i solutions/tx2/cpu/   -o results/tx2-cpu.csv   -l ../../data/LR-coefficients.json -p tx2 --include_only .json

# Add power measurements to the solutions

methods=( "HEUR" "ILP-IDLE-MAX" "ILP-IDLE-MIN" "ILP-SM-I" "QP-LR-UB" "BB-SM" "BB-LR" )
experiments=( "all" "cpu" )

for i in "${methods[@]}"; do
    for exp in "${experiments[@]}"; do
        python3 ../add_measured_data.py -r ./results/imx8a-$exp.csv -m ./measurements/imx8a/$exp/ -c power -e ../../data/environment-imx8a.json --measurement_suffix .json.yaml.csv
        python3 ../add_measured_data.py -r ./results/imx8a-$exp.csv -m ./measurements/imx8a/$exp/ -c temp-little -e ../../data/environment-imx8a.json --measurement_suffix .json.yaml.csv -d temperature --data_column "CPU_0_temp/m°C"
        python3 ../add_measured_data.py -r ./results/imx8a-$exp.csv -m ./measurements/imx8a/$exp/ -c temp-big -e ../../data/environment-imx8a.json --measurement_suffix .json.yaml.csv -d temperature --data_column "CPU_1_temp/m°C"
        python3 ../add_measured_data.py -r ./results/imx8a-$exp.csv -m ./measurements/imx8a/$exp/ -e ../../data/environment-imx8a.json --measurement_suffix .json.yaml.csv -d ambient

        python3 ../add_measured_data.py -r ./results/imx8b-$exp.csv -m ./measurements/imx8b/$exp/ -c power -e ../../data/environment-imx8b.json --measurement_suffix .json.yaml.csv
        python3 ../add_measured_data.py -r ./results/imx8b-$exp.csv -m ./measurements/imx8b/$exp/ -c temp-little -e ../../data/environment-imx8b.json --measurement_suffix .json.yaml.csv -d temperature --data_column "CPU_0_temp/m°C"
        python3 ../add_measured_data.py -r ./results/imx8b-$exp.csv -m ./measurements/imx8b/$exp/ -c temp-big -e ../../data/environment-imx8b.json --measurement_suffix .json.yaml.csv -d temperature --data_column "CPU_1_temp/m°C"
        python3 ../add_measured_data.py -r ./results/imx8b-$exp.csv -m ./measurements/imx8b/$exp/ -e ../../data/environment-imx8b.json --measurement_suffix .json.yaml.csv -d ambient

        python3 ../add_measured_data.py -r ./results/tx2-$exp.csv   -m ./measurements/tx2/$exp/   -c power -e ../../data/environment-tx2.json --measurement_suffix .json.yaml.csv
        python3 ../add_measured_data.py -r ./results/tx2-$exp.csv   -m ./measurements/tx2/$exp/   -c temp-little -e ../../data/environment-tx2.json --measurement_suffix .json.yaml.csv -d temperature --data_column "Cortex_A57_temp/m°C"
        python3 ../add_measured_data.py -r ./results/tx2-$exp.csv   -m ./measurements/tx2/$exp/   -c temp-big -e ../../data/environment-tx2.json --measurement_suffix .json.yaml.csv -d temperature --data_column "Denver2_temp/m°C"
        python3 ../add_measured_data.py -r ./results/tx2-$exp.csv   -m ./measurements/tx2/$exp/ -e ../../data/environment-tx2.json --measurement_suffix .json.yaml.csv -d ambient
    done 
done
