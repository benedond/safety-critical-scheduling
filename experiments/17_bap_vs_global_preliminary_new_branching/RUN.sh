#!/bin/bash

cd instances-05
echo "Running instances with 5 tasks"
./RUN.sh
cd ..

cd instances-10
echo "Running instances with 10 tasks"
./RUN.sh
cd ..

cd instances-15
echo "Running instances with 15 tasks"
./RUN.sh
cd ..

echo ====DONE====
