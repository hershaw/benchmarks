#!/bin/bash

git pull origin master

cd python-benchmarks

python benchmark.py pandas $1
echo '=========================================='
sleep 3
python benchmark.py sframe $1

cd ..
