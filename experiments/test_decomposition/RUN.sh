#!/bin/bash

python generate_instances.py generated-05 5 500
python generate_instances.py generated-10 10 50

cd generated-05
./RUN.sh
cd ..
cd generated-10
./RUN.sh
cd ..
echo ====DONE====
