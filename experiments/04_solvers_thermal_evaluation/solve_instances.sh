#!/bin/bash


solve () {
    EXP_PATH=$1

    mkdir -p ./solutions/$EXP_PATH
            
    for f in ./instances/$EXP_PATH/*; do
        echo "Processing $f"
        CURINST=$(basename $f)
        echo "Solving $CURINST"

        INPUT=./instances/$EXP_PATH/$CURINST

        for i in "${!solvers[@]}"; do
            echo "By ${solvers[i]}"
            OUTPUT=./solutions/$EXP_PATH/$CURINST-${solvers[i]}.json
            if [ -f $OUTPUT ]; then
                echo "Output file already exists."
            else
                python3 ../../tools/src/JSA-solvers/${EXP_PATHs[i]}/main.py --input $INPUT --output $OUTPUT --timelimit $timelimit ${cmds[i]} 2> $OUTPUT.err 1> $OUTPUT.log

                ./../../tools/bin/visualizer.exe --input $OUTPUT --output $OUTPUT.png
            fi
        done

    done
}
# ==============================================================================================

# Scalability and imx8 instances.
solvers=( "HEUR" "ILP-IDLE-MIN" "ILP-IDLE-MAX" "ILP-SM-I" "ILP-SM-II" "QP-LR-UB")
EXP_PATHs=( "HEUR" "ILP-IDLE" "ILP-IDLE" "ILP-SM-I" "ILP-SM-II" "QP-LR-UB")
timelimit=300

cmds=( "" "" "--maximize" "" "" "--path_lr ../../data/LR-coefficients.json -p imx8a")
solve "imx8a/all"
solve "imx8a/cpu"

cmds=( "" "" "--maximize" "" "" "--path_lr ../../data/LR-coefficients.json -p imx8b")
solve "imx8b/all"
solve "imx8b/cpu"

cmds=( "" "" "--maximize" "" "" "--path_lr ../../data/LR-coefficients.json -p tx2")
solve "tx2/all"
solve "tx2/cpu"

