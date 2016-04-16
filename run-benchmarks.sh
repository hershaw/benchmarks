#!/bin/bash

python python-benchmarks/pandas-benchmark.py
echo "=============================================="
python python-benchmarks/sframe-benchmark.py
echo "=============================================="
node --max_old_space_size=4096 node-benchmarks/node-benchmark.js
