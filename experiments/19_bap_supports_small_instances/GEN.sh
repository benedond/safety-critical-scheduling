#!/bin/bash

python generate_instances.py instances-05 05 25
chmod +x ./instances-05/RUN.sh

python generate_instances.py instances-10 10 100
chmod +x ./instances-10/RUN.sh


