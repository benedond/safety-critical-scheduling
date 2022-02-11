#!/bin/bash

N=10
SIZE="20 22 24 26 28 30 32 34 36"
for i in $(eval echo "{1..$N}"); do
    for n in ${SIZE}; do
        echo "IN_${n}_$i"
        ./../../tools/bin/instance_generator.exe --environment ./data/environment-imx8.json --benchmark-data ./data/characteristics-imx8a-all.csv --task-count ${n} --output ./instances/scalability_ilp_20-36/imx8a/IN_${n}_$i.json
    done
done