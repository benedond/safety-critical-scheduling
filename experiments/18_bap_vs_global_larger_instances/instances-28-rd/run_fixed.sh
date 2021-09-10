#!/bin/bash
for i in *.json
do
    echo $i    
    if [ ! -f $i-bap-RecFixed.out ]; then
        ../../../tools/src/decomposed_solver_copy/main.py --input $i --output $i-bap-RecFixed.out --log --branching tasks --timelimit 600 2> $i-bap-RecFixed.err 1> $i-bap-RecFixed.log
        ../../../tools/bin/visualizer.exe --input $i-bap-RecFixed.out --output $i-bap-RecFixed.png
    fi 
done