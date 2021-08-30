#!/bin/bash
for i in *.json
do
    echo $i    
    if [ ! -f $i-bap-mm.out ]; then
        ../../../tools/src/decomposed_solver_copy/main.py --input $i --output $i-bap-mm.out --log --branching tasks --timelimit 600 2> $i-bap-mm.err 1> $i-bap-mm.log
        ../../../tools/bin/visualizer.exe --input $i-bap-mm.out --output $i-bap-mm.png
    fi 
done