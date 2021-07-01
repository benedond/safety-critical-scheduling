#!/bin/bash

for i in *.json
do
	echo $i
	../../../tools/bin/ilp_global_solver.exe --input $i --output $i.out
done
