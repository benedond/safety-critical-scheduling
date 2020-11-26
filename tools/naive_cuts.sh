#!/bin/bash

ITERATION_LIMIT=1000
SOLUTION_FILE=$2

cp $1 $SOLUTION_FILE

for i in $(seq $ITERATION_LIMIT); do
	ilp_res_assigner.exe --input $SOLUTION_FILE --output $SOLUTION_FILE --no-iis-output

	if [ $? -eq 2 ]; then
		echo resource assignment failed, iteration: $i
		exit
	fi

	ilp_solver.exe --input $SOLUTION_FILE --output $SOLUTION_FILE --no-iis-output --generate-naive-cuts

	if [ $? -eq 0 ]; then
		echo solution found, iteration: $i
		exit
	fi
done

echo iteration limit reached