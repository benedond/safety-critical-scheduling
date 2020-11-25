@ECHO OFF
cd bin

generator --environment ../../data/environment.json --min-length 5 --max-length 35 --task-count 15 | solver | visualiser-display --display
