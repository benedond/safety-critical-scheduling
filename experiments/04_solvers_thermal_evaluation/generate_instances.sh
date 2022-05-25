#!/bin/bash

# Instances for thermal comparison
N=6

mkdir -p instances/imx8a/all
mkdir -p instances/imx8a/cpu
mkdir -p instances/imx8b/all
mkdir -p instances/imx8b/cpu
mkdir -p instances/tx2/all
mkdir -p instances/tx2/cpu

# generate only cpu-bound instances
for i in $(eval echo "{1..$N}"); do
    ./../../tools/bin/instance_generator.exe --environment ../../data/environment-imx8a.json --benchmark-data ../../data/characteristics-imx8a-cpu.csv --output ./instances/imx8a/cpu/IN_$i.json --seed $i
    ./../../tools/bin/instance_generator.exe --environment ../../data/environment-imx8b.json --benchmark-data ../../data/characteristics-imx8b-cpu.csv --output ./instances/imx8b/cpu/IN_$i.json --seed $i
    ./../../tools/bin/instance_generator.exe --environment ../../data/environment-tx2.json --benchmark-data ../../data/characteristics-tx2-cpu.csv --output ./instances/tx2/cpu/IN_$i.json --seed $i
done

# generate mix of cpu and mem instances
for i in $(eval echo "{1..$N}"); do
    ./../../tools/bin/instance_generator.exe --environment ../../data/environment-imx8a.json --benchmark-data ../../data/characteristics-imx8a-all.csv --output ./instances/imx8a/all/IN_$i.json --seed $i
    ./../../tools/bin/instance_generator.exe --environment ../../data/environment-imx8b.json --benchmark-data ../../data/characteristics-imx8b-all.csv --output ./instances/imx8b/all/IN_$i.json --seed $i
    ./../../tools/bin/instance_generator.exe --environment ../../data/environment-tx2.json --benchmark-data ../../data/characteristics-tx2-all.csv --output ./instances/tx2/all/IN_$i.json --seed $i
done
