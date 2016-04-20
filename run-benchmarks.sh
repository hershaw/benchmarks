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
    python python_benchmarks/benchmark.py -l $l -d $d -b get_random_stats -t large -n $nruns
    python python_benchmarks/benchmark.py -l $l -d "$l"_"$d" -b get_random_cols -t large -n $nruns
  done
done
