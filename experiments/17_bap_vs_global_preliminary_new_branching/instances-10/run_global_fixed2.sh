#!/bin/bash
for i in *.json
do
    echo $i
    if [ ! -f $i-global-fixed2.out ]; then
        ../../../tools/src/ilp_global_solver/main.py --input $i --output $i-global-fixed2.out --fixed --timelimit 600 2> $i-global-fixed2.err 1> $i-global-fixed2.log
        ../../../tools/bin/visualizer.exe --input $i-global-fixed2.out --output $i-global-fixed2.png  
    fi  
done