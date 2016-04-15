# benchmarks

## Comparing node.js, pandas, and sframe

### Motivation

When preparing data for building credit risk classifiers for small to medium size banks, most of the operations reduce to
filtering (removing rows) or transforming (binning categoricals) in tabular data of < 1,000,000 entries.

### Setup

In this repository, two simple transformations have been specified in exactly the format we use in production.
They are one "drop" operation in which you must remove all rows that have a set of values for a particular column and
one "combine" command which just bins two values into a single value. Most of our UX bottle necks (because of execution time)
reduce to these operations.

### The competitors

There are two python implementations and one node.js implementation located in:

- `python-benchmarks/sframe-benchmark.py`
- `python-benchmarks/pandas-benchmark.py`
- NUNO: FILL THIS OUT

### Install

#### python
In `python-benchmarks/` there is a pip-requirements file. Create a virtual environment and `pip install`.

#### node

NUNO, FILL ME IN!!!

### Run

`./run-benchmarks.sh`

A lot of stuff is printed, the important lines are the ones that display the total time taken to apply both operations:

- `pandas apply transforms`
- `sframe apply transforms`
- `NUNO FILL ME IN`
