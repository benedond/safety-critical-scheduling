#!/bin/bash
rm stats.csv
python3 ../../tools/src/statistics/generate_csv.py --folder ./generated --output stats.csv
echo ====DONE====
