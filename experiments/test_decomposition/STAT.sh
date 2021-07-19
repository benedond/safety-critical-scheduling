#!/bin/bash
rm stats.csv
python ../../tools/src/statistics/generate_csv.py --folder ./generated --output stats.csv
echo ====DONE====
