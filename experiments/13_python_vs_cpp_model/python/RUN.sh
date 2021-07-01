#!/bin/bash

for i in *.json
do
	echo $i
	../../../tools/src/ilp_global_solver/main.py --input $i --output $i.out
done
