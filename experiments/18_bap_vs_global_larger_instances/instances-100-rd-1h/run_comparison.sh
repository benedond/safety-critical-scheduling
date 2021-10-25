#!/bin/bash

# global-fixed2
for i in *.json
do
    echo $i
    if [ ! -f $i-global-fixed2.out ]; then
        ../../../tools/src/ilp_global_solver/main.py --input $i --output $i-global-fixed2.out --fixed --timelimit 3600 2> $i-global-fixed2.err 1> $i-global-fixed2.log
        ../../../tools/bin/visualizer.exe --input $i-global-fixed2.out --output $i-global-fixed2.png  
    fi  
done

# support
for i in *.json
do
    echo $i    
    if [ ! -f $i-bap-support.out ]; then
        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap-support.out --log --branching supports --timelimit 3600 2> $i-bap-support.err 1> $i-bap-support.log
        ../../../tools/bin/visualizer.exe --input $i-bap-support.out --output $i-bap-support.png
    fi 
done

# support depth 20%
#!/bin/bash
for i in *.json
do
    echo $i    
    if [ ! -f $i-bap-support-d20.out ]; then
        ../../../tools/src/decomposed_solver/main.py --input $i --output $i-bap-support-d20.out --log --branching supports --timelimit 3600 --depth 20 2> $i-bap-support-d20.err 1> $i-bap-support-d20.log
        ../../../tools/bin/visualizer.exe --input $i-bap-support-d20.out --output $i-bap-support-d20.png
    fi 
done