#!/bin/bash

cd instances-35-rd
echo "Running instances with 35 tasks"
./run_comparison.sh
cd ..

cd instances-45-rd
echo "Running instances with 45 tasks"
./run_comparison.sh
cd ..

cd instances-55-rd
echo "Running instances with 55 tasks"
./run_comparison.sh
cd ..

cd instances-100-rd
echo "Running instances with 100 tasks"
./run_comparison.sh
cd ..

echo ====DONE====
