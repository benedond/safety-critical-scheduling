#!/bin/bash

set -euo pipefail

run () {
    INPATH=$1
    OUTPATH=$2
    PLAT=$3
    TIM=$4    

    #for i in {0..5}; do
    #    echo 1 > /sys/devices/system/cpu/cpu$i/online
    #done

    # turn off the fan
    echo 0 > /sys/kernel/debug/tegra_fan/target_pwm

    mkdir -p $OUTPATH

    for benchmark in $INPATH/*; do
        CURBENCH=$(basename $benchmark)

        echo "Processing $CURBENCH"

        if [ -f $OUTPATH/$CURBENCH.csv ]; then
            echo "Output file already exists."
        else
            cd /root/thermobench/build/benchmarks/autobench_2.0/single/
	    thermobench --verbose --time=$TIM --wait=50 --wait-timeout=60 --sensors_file=/root/thermobench/src/sensors.$PLAT --cpu-usage --column=CPU{0,1,2,3,4,5}_work_done --output=$OUTPATH/$CURBENCH.csv -- demos-sched -p high -c $INPATH/$CURBENCH
        fi
    done
}
# ===================================================================================================

ulimit -n 10000

run "$@"
