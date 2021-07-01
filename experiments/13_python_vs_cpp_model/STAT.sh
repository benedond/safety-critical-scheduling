#!/bin/bash
rm stats.csv
python ../../tools/src/statistics/generate_csv.py --folder ./python --output stats.csv
python ../../tools/src/statistics/generate_csv.py --folder ./python_gen --output stats.csv
python ../../tools/src/statistics/generate_csv.py --folder ./cpp --output stats.csv
echo ====DONE====
