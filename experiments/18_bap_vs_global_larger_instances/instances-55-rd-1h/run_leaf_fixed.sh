#!/bin/bash
for i in *.json
do
    echo $i    
    if [ ! -f $i-bap-Leaf.out ]; then
        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap-Leaf.out --log --branching tasks --timelimit 3600 2> $i-bap-Leaf.err 1> $i-bap-Leaf.log
        ../../../tools/bin/visualizer.exe --input $i-bap-Leaf.out --output $i-bap-Leaf.png
    fi 
done