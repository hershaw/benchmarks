#!/bin/bash

python python-benchmarks/pandas-benchmark.py
python python-benchmarks/sframe-benchmark.py
node --max_old_space_size=4096 node-benchmarks/node-benchmark.js
