#!/bin/bash

for i in *.json
do
	echo $i
	../../../tools/src/ilp_global_solver/main.py --input $i --output $i-global.out
	../../../tools/bin/visualizer.exe --input $i-global.out --output $i-global.png

	../../../tools/src/ilp_global_solver_gen/main.py --input $i --output $i-global-gen.out
	../../../tools/bin/visualizer.exe --input $i-global-gen.out --output $i-global-gen.png

	../../../tools/bin/assignment_solver.exe --input $i --output $i-ref.ass
	../../../tools/bin/schedule_solver.exe --input $i-ref.ass --output $i-sch.out
	../../../tools/bin/visualizer.exe --input $i-sch.out --output $i-sch.png

	../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap.out
	../../../tools/bin/visualizer.exe --input $i-bap.out --output $i-bap.png
done
