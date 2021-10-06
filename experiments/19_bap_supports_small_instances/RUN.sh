#!/bin/bash

cd instances-05
echo "Running instances with 05 tasks"
./RUN.sh
cd ..

cd instances-10
echo "Running instances with 10 tasks"
./RUN.sh
cd ..

echo ====DONE====
