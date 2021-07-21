#!/bin/bash
rm stats*.csv

python3 ../../tools/src/statistics/generate_csv.py --folder ./generated-05 --output stats-05.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./generated-10 --output stats-10.csv

python3 test.py stats-05.csv 500
python3 test.py stats-10.csv 50

echo ====DONE====
