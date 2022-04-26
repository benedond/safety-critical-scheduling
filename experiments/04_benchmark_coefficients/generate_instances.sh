#!/bin/bash

python generate_instances.py -e ../../data/environment-imx8a.json -b ../../data/benchmarks.csv -o instances/imx8a/
python generate_instances.py -e ../../data/environment-imx8b.json -b ../../data/benchmarks.csv -o instances/imx8b/
python generate_instances.py -e ../../data/environment-tx2.json -b ../../data/benchmarks.csv -o instances/tx2/