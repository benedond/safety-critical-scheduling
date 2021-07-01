#!/bin/bash

for i in *.json
do
	echo $i
	../../../tools/src/ilp_global_solver_gen/main.py --input $i --output $i.out
done
