#!/bin/bash

export_config () {
    INST_PATH=$1
    
    mkdir -p ./demos_configurations/$INST_PATH
    mkdir -p ./schedules/$INST_PATH
            
    for f in ./instances/$INST_PATH/*; do
        CURINST=$(basename $f)    
        ./../../tools/bin/demos_config_export.exe --input $f --output ./demos_configurations/$INST_PATH/$CURINST.yaml
        ./../../tools/bin/visualizer.exe --input $f --output ./schedules/$INST_PATH/$CURINST.png
    done
}

export_config "imx8a/all"
export_config "imx8a/cpu"