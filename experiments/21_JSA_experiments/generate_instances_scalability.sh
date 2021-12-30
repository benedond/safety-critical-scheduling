#!/bin/bash

N=10
SIZE="5 10 15 20 25 30 35 40 45 50 55 60"
for i in $(eval echo "{1..$N}"); do
    for n in ${SIZE}; do
        echo "IN_${n}_$i"
        ./../../tools/bin/instance_generator.exe --environment ./data/environment-imx8.json --benchmark-data ./data/characteristics-imx8a-all.csv --task-count ${n} --output ./instances/scalability/imx8a/IN_${n}_$i.json
    done
done