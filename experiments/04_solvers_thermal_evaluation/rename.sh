#!/bin/bash

# Just for the renaming of old solutions to desired format (when generating solutions from the scratch, the renaming should be already part of the procedure)

solvers=( "HEUR" "ILP-IDLE-MIN" "ILP-IDLE-MAX" "ILP-SM-I" "ILP-SM-II" "QP-LR-UB")
folders=( "solutions" "demos_configurations" "measurements" )

# Rename the solved instances
for i in "${solvers[@]}"; do
    for f in "${folders[@]}"; do
        rename 's/.json-'"$i"'/-'"$i"'/' $f/imx8a/all/*
        rename 's/.json-'"$i"'/-'"$i"'/' $f/imx8a/cpu/*
        rename 's/.json-'"$i"'/-'"$i"'/' $f/imx8b/all/*
        rename 's/.json-'"$i"'/-'"$i"'/' $f/imx8b/cpu/*
        rename 's/.json-'"$i"'/-'"$i"'/' $f/tx2/all/*
        rename 's/.json-'"$i"'/-'"$i"'/' $f/tx2/cpu/*
    done
done
