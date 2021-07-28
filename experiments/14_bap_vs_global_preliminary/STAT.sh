#!/bin/bash
rm stats*.csv

python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-05 --output stats-05.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-10 --output stats-10.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-15 --output stats-15.csv

echo ====DONE====
