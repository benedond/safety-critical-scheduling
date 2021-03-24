#!/bin/bash

for i in *.json
do
	~/dp-safety-critical-scheduling/tools/bin/ilp_global_solver.exe --input $i --output $i.out --method eik
done
