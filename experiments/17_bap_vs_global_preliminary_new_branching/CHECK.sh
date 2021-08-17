#!/bin/bash

echo "Checking instances-05"
python3 test.py stats-05.csv 100

echo "Checking instances-10"
python3 test.py stats-10.csv 100

echo "Checking instances-15"
python3 test.py stats-15.csv 100


