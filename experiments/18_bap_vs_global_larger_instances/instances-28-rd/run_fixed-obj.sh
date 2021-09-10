#!/bin/bash
for i in *.json
do
    echo $i    
    if [ ! -f $i-bap-RecFixedObj.out ]; then
        ../../../tools/src/decomposed_solver_copy/main.py --input $i --output $i-bap-RecFixedObj.out --log --branching tasks --timelimit 600 2> $i-bap-RecFixedObj.err 1> $i-bap-RecFixedObj.log
        ../../../tools/bin/visualizer.exe --input $i-bap-RecFixedObj.out --output $i-bap-RecFixedObj.png
    fi 
done