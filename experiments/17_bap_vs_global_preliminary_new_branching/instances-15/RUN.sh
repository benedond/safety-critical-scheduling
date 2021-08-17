#!/bin/bash
for i in *.json
do
    echo $i
    if [ ! -f $i-global.out ]; then
        ../../../tools/src/ilp_global_solver/main.py --input $i --output $i-global.out 2> $i-global.err 1> $i-global.log
        ../../../tools/bin/visualizer.exe --input $i-global.out --output $i-global.png
    fi 
    if [ ! -f $i-bap_pair.out ]; then
        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap_pair.out --log 2> $i-bap_pair.err 1> $i-bap_pair.log
        ../../../tools/bin/visualizer.exe --input $i-bap_pair.out --output $i-bap_pair.png
    fi 
    if [ ! -f $i-bap_task.out ]; then
        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap_task.out --log --branching tasks 2> $i-bap_task.err 1> $i-bap_task.log
        ../../../tools/bin/visualizer.exe --input $i-bap_task.out --output $i-bap_task.png
    fi 
done