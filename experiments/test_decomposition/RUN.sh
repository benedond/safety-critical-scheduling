#!/bin/bash

python generate_instances.py generated 5 10

cd generated
./RUN.sh
cd ..
echo ====DONE====
