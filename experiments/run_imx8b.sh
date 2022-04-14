#!/bin/bash

run () {
    INPATH=$1
    OUTPATH=$2
    PLAT=$3
	TIM=$4
        
    mkdir -p $OUTPATH
	
	for benchmark in $INPATH/*; do
		CURBENCH=$(basename $benchmark)
		echo "Processing $CURBENCH"
	
		if [ -f $OUTPATH/$CURBENCH.csv ]; then
				echo "Output file already exists."
		else	
			cd /root/thermobench/build/benchmarks/autobench_2.0/single/
			thermobench --verbose --time=$TIM --wait=50 --wait-timeout=60 --sensors_file=/root/thermobench/src/sensors.$PLAT --cpu-usage --column=CPU0_work_done --column=CPU1_work_done --column=CPU2_work_done --column=CPU3_work_done --column=CPU4_work_done --column=CPU5_work_done --output=$OUTPATH/$CURBENCH.csv -- demos-sched -p per_process -c $INPATH/$CURBENCH
		fi
	done	
}
# ===================================================================================================

INPUT_PATH=$1
OUTPUT_PATH=$2
PLATFORM=$3
TIME=$4

ulimit -n 10000

run "$INPUT_PATH" "$OUTPUT_PATH" "$PLATFORM" "$TIME"