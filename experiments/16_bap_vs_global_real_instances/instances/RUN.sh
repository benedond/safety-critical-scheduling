#!/bin/bash
for i in *.json
do
    echo $i
    if [ ! -f $i-global.out ]; then
        ../../../tools/src/ilp_global_solver/main.py --input $i --output $i-global.out --timelimit 60 2> $i-global.err 1> $i-global.log
        ../../../tools/bin/visualizer.exe --input $i-global.out --output $i-global.png
    fi 
    if [ ! -f $i-bap-pair.out ]; then
        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap-pair.out --log --timelimit 60 2> $i-bap-pair.err 1> $i-bap-pair.log
        ../../../tools/bin/visualizer.exe --input $i-bap-pair.out --output $i-bap-pair.png
    fi 

    if [ ! -f $i-bap-task.out ]; then
        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap-task.out --log --timelimit 60 --branching tasks 2> $i-bap-task.err 1> $i-bap-task.log
        ../../../tools/bin/visualizer.exe --input $i-bap-task.out --output $i-bap-task.png
    fi 
done
