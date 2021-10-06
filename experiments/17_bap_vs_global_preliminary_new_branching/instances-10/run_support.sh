#!/bin/bash
for i in *.json
do
    echo $i    
    if [ ! -f $i-bap-support.out ]; then
        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap-support.out --log --branching supports --timelimit 600 2> $i-bap-support.err 1> $i-bap-support.log
        ../../../tools/bin/visualizer.exe --input $i-bap-support.out --output $i-bap-support.png
    fi 
done