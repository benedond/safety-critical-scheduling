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

python generate_instances.py instances-35-rd 35 10 True
chmod +x ./instances-35-rd/RUN.sh

python generate_instances.py instances-45-rd 45 10 True
chmod +x ./instances-45-rd/RUN.sh

python generate_instances.py instances-55-rd 55 10 True
chmod +x ./instances-55-rd/RUN.sh

python generate_instances.py instances-100-rd 100 10 True
chmod +x ./instances-100-rd/RUN.sh
