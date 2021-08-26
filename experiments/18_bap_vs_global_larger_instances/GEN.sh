#!/bin/bash

python generate_instances.py instances-22 22 25
chmod +x ./instances-22/RUN.sh

python generate_instances.py instances-25 25 25
chmod +x ./instances-25/RUN.sh

python generate_instances.py instances-28 28 25
chmod +x ./instances-28/RUN.sh

python generate_instances.py instances-22-rd 22 25 True
chmod +x ./instances-22-rd/RUN.sh

python generate_instances.py instances-25-rd 25 25 True
chmod +x ./instances-25-rd/RUN.sh

python generate_instances.py instances-28-rd 28 25 True
chmod +x ./instances-28-rd/RUN.sh
