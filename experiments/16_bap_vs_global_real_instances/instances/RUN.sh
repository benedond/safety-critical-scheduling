#!/bin/bash
for i in *.json
do
    echo $i
    if [ ! -f $i-global.out ]; then
        ../../../tools/src/ilp_global_solver/main.py --input $i --output $i-global.out --timelimit 60 2> $i-global.err 1> $i-global.log
        ../../../tools/bin/visualizer.exe --input $i-global.out --output $i-global.png
    fi 
    if [ ! -f $i-bap.out ]; then
        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap.out --log --timelimit 60 2> $i-bap.err 1> $i-bap.log
        ../../../tools/bin/visualizer.exe --input $i-bap.out --output $i-bap.png
    fi 
done