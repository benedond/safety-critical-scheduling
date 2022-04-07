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
            OUTPUT=./solutions/$EXP_PATH/$CURINST-${solvers[i]}.out
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
cmds=( "" "" "--maximize" "" "" "")
timelimit=300
solve "scalability/imx8a"


# Only ILP models with longer timescale
solvers=( "ILP-SM-I" "ILP-SM-II" )
EXP_PATHs=( "ILP-SM-I" "ILP-SM-II" )
cmds=( "" "" )
timelimit=1200
solve "scalability_ilp_20-36/imx8a"
solve "scalability_ilp/imx8a"
