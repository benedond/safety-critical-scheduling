#!/bin/bash

AUTOBENCH_HOME="/root/thermobench/build/benchmarks/autobench_2.0/single"

# Parameters of cluster 0
CLUSTER_0_FREQUENCIES="1200"
CLUSTER_0_MIN_FREQ="600MHz"
CLUSTER_0_MAX_FREQ="1200MHz"
CLUSTER_0_CORE="0"
CLUSTER_0_CORES="0 1 2 3"
CLUSTER_0_MAX_CORES="4"
# Parameters of cluster 1
CLUSTER_1_FREQUENCIES="1596"
CLUSTER_1_MIN_FREQ="600MHz"
CLUSTER_1_MAX_FREQ="1596MHz"
CLUSTER_1_CORE="4"
CLUSTER_1_CORES="4 5"
CLUSTER_1_MAX_CORES="2"

run () {
    INPATH=$1
    OUTPATH=$2
    PLAT=$3
        
    mkdir -p $OUTPATH
	
	# Make all cores running
	for i in {0..5}; do
			echo 1 > /sys/devices/system/cpu/cpu$i/online
	done

	cpufreq-set -g userspace
	# set frequencies to max
	cpufreq-set -c $CLUSTER_0_CORE -d $CLUSTER_0_MAX_FREQ -u $CLUSTER_0_MAX_FREQ
	cpufreq-set -c $CLUSTER_1_CORE -d $CLUSTER_1_MAX_FREQ -u $CLUSTER_1_MAX_FREQ 

	for benchmark in $INPATH/*; do
		CURBENCH=$(basename $benchmark)
		echo "Processing $CURBENCH"
	
		if [ -f $OUTPATH/$CURBENCH.csv ]; then
				echo "Output file already exists."
		else	
	        cd $AUTOBENCH_HOME
			thermobench --verbose --time=10 --fan-cmd=fan --fan-on=0 --wait=50 --wait-timeout=60 --sensors_file=/root/thermobench/src/sensors.$PLAT --cpu-usage --column=CPU0_work_done --column=CPU1_work_done --column=CPU2_work_done --column=CPU3_work_done --column=CPU4_work_done --column=CPU5_work_done --output=$OUTPATH/$CURBENCH.csv -- demos-sched -p per_process -c $INPATH/$CURBENCH
		fi
	done

	cpufreq-set -c $CLUSTER_0_CORE -d $CLUSTER_0_MIN_FREQ -u $CLUSTER_0_MAX_FREQ
	cpufreq-set -c $CLUSTER_1_CORE -d $CLUSTER_1_MIN_FREQ -u $CLUSTER_1_MAX_FREQ 
	cpufreq-set -g ondemand	
}
# ===================================================================================================

INPUT_PATH=$1
OUTPUT_PATH=$2
PLATFORM=$3

ulimit -n 10000

run "$INPUT_PATH" "$OUTPUT_PATH" "$PLATFORM"