#!/bin/bash

python generate_instances.py -e ../../data/environment-imx8.json -b ../../data/benchmarks.csv -o instances/imx8/
python generate_instances.py -e ../../data/environment-tx2.json -b ../../data/benchmarks.csv -o instances/tx2/