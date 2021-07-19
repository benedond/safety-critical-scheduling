#!/bin/bash

for i in *.json
do
	echo $i
	../../../tools/src/ilp_global_solver_gen/main.py --input $i --output $i-global.out
	../../../tools/bin/visualizer.exe --input $i-global.out --output $i-global.png

	../../../tools/bin/assignment_solver.exe --input $i --output $i-ref.ass
	../../../tools/bin/schedule_solver.exe --input $i-ref.ass --output $i-sch.out
	../../../tools/bin/visualizer.exe --input $i-sch.out --output $i-sch.png
done
