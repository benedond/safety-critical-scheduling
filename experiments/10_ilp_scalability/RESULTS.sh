#!/bin/bash
for i in modpred/*.out
do
	~/dp-safety-critical-scheduling/tools/bin/stat.exe --input $i
done

for i in eik/*.out 
do
	~/dp-safety-critical-scheduling/tools/bin/stat.exe --input $i 
done

for i in nob/*.out
do
	~/dp-safety-critical-scheduling/tools/bin/stat.exe --input $i 
done
