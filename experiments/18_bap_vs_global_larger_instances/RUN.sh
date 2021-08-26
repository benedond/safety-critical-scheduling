#!/bin/bash

cd instances-22
echo "Running instances with 22 tasks"
./RUN.sh
cd ..

cd instances-25
echo "Running instances with 25 tasks"
./RUN.sh
cd ..

cd instances-28
echo "Running instances with 28 tasks"
./RUN.sh
cd ..

cd instances-22-rd
echo "Running instances with 22 tasks (RD)"
./RUN.sh
cd ..

cd instances-25-rd
echo "Running instances with 25 tasks (RD)"
./RUN.sh
cd ..

cd instances-28-rd
echo "Running instances with 28 tasks (RD)"
./RUN.sh
cd ..

echo ====DONE====
