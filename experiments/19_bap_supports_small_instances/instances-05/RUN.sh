#!/bin/bash
for i in *.json
do
    echo $i
    if [ ! -f $i-global.out ]; then
        ../../../tools/src/ilp_global_solver/main.py --input $i --output $i-global.out --fixed --timelimit 600 2> $i-global.err 1> $i-global.log
        ../../../tools/bin/visualizer.exe --input $i-global.out --output $i-global.png
    fi 
    if [ ! -f $i-bap.out ]; then
        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap.out --log --branching supports --timelimit 600 2> $i-bap.err 1> $i-bap.log
        ../../../tools/bin/visualizer.exe --input $i-bap.out --output $i-bap.png
    fi 
    if [ ! -f $i-bap-task.out ]; then
        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap-task.out --log --branching tasks --timelimit 600 2> $i-bap-task.err 1> $i-bap-task.log
        ../../../tools/bin/visualizer.exe --input $i-bap-task.out --output $i-bap-task.png
    fi 
done