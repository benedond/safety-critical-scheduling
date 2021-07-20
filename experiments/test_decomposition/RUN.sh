#!/bin/bash

python generate_instances.py generated 5 100

cd generated
./RUN.sh
cd ..
echo ====DONE====
