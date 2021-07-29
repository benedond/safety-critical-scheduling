#!/bin/bash

cd generator
python instance_gen.py

cp IN_*.json ../instances

cd ..

