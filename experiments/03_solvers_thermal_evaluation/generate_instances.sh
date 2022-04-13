#!/bin/bash

# Instances for thermal comparison
N=6

# generate only cpu-bound instances
for i in $(eval echo "{1..$N}"); do
    ./../../tools/bin/instance_generator.exe --environment ../../data/environment-imx8.json --benchmark-data ../../data/characteristics-imx8a-cpu.csv --output ./instances/imx8a/cpu/IN_$i.json
done

# generate mix of cpu and mem instances
for i in $(eval echo "{1..$N}"); do
    ./../../tools/bin/instance_generator.exe --environment ../../data/environment-imx8.json --benchmark-data ../../data/characteristics-imx8a-all.csv --output ./instances/imx8a/all/IN_$i.json
done
