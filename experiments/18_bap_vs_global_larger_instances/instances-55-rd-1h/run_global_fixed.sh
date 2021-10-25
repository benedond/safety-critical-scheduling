#!/bin/bash
for i in *.json
do
    echo $i
    if [ ! -f $i-global-fixed.out ]; then
        ../../../tools/src/ilp_global_solver/main.py --input $i --output $i-global-fixed.out --fixed --timelimit 3600 2> $i-global-fixed.err 1> $i-global-fixed.log
        ../../../tools/bin/visualizer.exe --input $i-global-fixed.out --output $i-global-fixed.png  
    fi  
done