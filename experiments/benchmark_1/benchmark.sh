#!/bin/bash

./stat.exe --no-input --write-header >benchmark.csv

for task_length in `seq 1000 1000 100000` 
do
	echo -n "$task_length" >>benchmark.csv
	./generator.exe --environment benchmark_environment.json --task-count $task_length --min-length 5 --max-length 10000 | ./solver.exe | ./stat.exe >>benchmark.csv
done
