#!/bin/bash

git pull origin master

datasets="
lc
lc_big
lc_huge
"

libs="
pandas
sframe
"

nruns=1

for d in $datasets
do
  for l in $libs
  do
    python python_benchmarks/benchmark.py -l $l -d $d -b apply_index_and_write
    python python_benchmarks/benchmark.py -l $l -d "$l"_"$d" -b get_random_stats -t large -n $nruns
    python python_benchmarks/benchmark.py -l $l -d "$l"_"$d" -b get_random_cols -t large -n $nruns
  done
  node --max_old_space_size=28000 node-benchmarks/index.js $d large apply_index $nruns
  node --max_old_space_size=28000 node-benchmarks/index.js $d large get_cols $nruns
  node --max_old_space_size=28000 node-benchmarks/index.js $d large calculate_stats $nruns
done
