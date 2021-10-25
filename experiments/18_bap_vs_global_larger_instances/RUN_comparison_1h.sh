#!/bin/bash

cd instances-55-rd-1h
echo "Running instances with 55 tasks"
./run_comparison.sh
cd ..

cd instances-100-rd-1h
echo "Running instances with 100 tasks"
./run_comparison.sh
cd ..

echo ====DONE====
