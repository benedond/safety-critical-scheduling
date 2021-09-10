#!/bin/bash
rm stats*.csv

python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-22 --output stats-22.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-25 --output stats-25.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-28 --output stats-28.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-22-rd --output stats-22-rd.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-25-rd --output stats-25-rd.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-28-rd --output stats-28-rd.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-35-rd --output stats-35-rd.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-45-rd --output stats-45-rd.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-55-rd --output stats-55-rd.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./instances-100-rd --output stats-100-rd.csv

echo ====DONE====
