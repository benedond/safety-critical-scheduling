#!/bin/bash

export_config () {
    INST_PATH=$1
    
    mkdir -p ./demos_configurations/$INST_PATH
    mkdir -p ./schedules/$INST_PATH
            
    for f in ./instances/$INST_PATH/*; do
        CURINST=$(basename $f)    
        
        if [ -f ./demos_configurations/$INST_PATH/$CURINST.yaml ]; then
          echo "Output file already exists."
        else
            ./../../tools/bin/demos_config_export.exe --input $f --output ./demos_configurations/$INST_PATH/$CURINST.yaml
            # Fix cwd to be able to change dir before running
            echo "set_cwd: false" | cat - ./demos_configurations/$INST_PATH/$CURINST.yaml > /tmp/out && mv /tmp/out ./demos_configurations/$INST_PATH/$CURINST.yaml
            ./../../tools/bin/visualizer.exe --input $f --output ./schedules/$INST_PATH/$CURINST.png
        fi
    done
}

export_config "scale-1x/imx8a/all"
export_config "scale-1x/imx8a/cpu"
export_config "scale-1x/imx8b/all"
export_config "scale-1x/imx8b/cpu"

export_config "scale-3x/imx8a/all"
export_config "scale-3x/imx8a/cpu"
export_config "scale-3x/imx8b/all"
export_config "scale-3x/imx8b/cpu"

export_config "scale-10x/imx8b/all"
export_config "scale-10x/imx8b/cpu"