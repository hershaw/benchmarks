# import os
from util import timer
from index import index
from transforms import transforms
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    '--lib',
    help='Library to use.', type=str, choices=['pandas', 'sframe'],
    required=True)
parser.add_argument(
    '--dataset', help='Which dataset to use', type=str, required=True)
parser.add_argument(
    '--transforms', help='Which set of transforms to run', type=str,
    choices=['small', 'medium', 'large'], required=False)
parser.add_argument(
    '--benchmark', help='Which benchmark to use.', type=str,
    choices=['apply_index_and_write', 'get_random_cols',
             'get_random_stats'],
    required=True)


args = parser.parse_args()


def realpath(fname):
    return './data/{}'.format(fname)


def run_benchmark(libname, filename, benchmarks):
    if libname == 'pandas':
        import pandas_benchmark as module
    elif libname == 'sframe':
        import sframe_benchmark as module

    timer.start('{}-load'.format(libname))
    frame = module.load_file(realpath(filename))
    timer.end('{}-load'.format(libname))

    timer.start('{}-total'.format(libname))
    for funcname, args in benchmarks:
        timer.start('{}-{}'.format(libname, funcname))
        frame = getattr(module, funcname)(frame, *args)
        timer.end('{}-{}'.format(libname, funcname))
    print('+++++++++++++++++++++++++++++++')
    timer.end('{}-total'.format(libname))
    print('+++++++++++++++++++++++++++++++')
    print('the "total" time DOES not include file read time')


if __name__ == '__main__':
    lib = args.lib
    dataset = args.dataset
    benchmark = args.benchmark
    transforms = transforms[args.transforms] if args.transforms else None
    if args.benchmark != 'apply_index_and_write' and transforms is None:
        raise ValueError('transforms required for {}'.format(args.benchmark))
    benchmarks = {
        'apply_index_and_write': [
            ('apply_index', [index]),
            ('to_file', [realpath('{}_{}'.format(lib, dataset))]),
        ],
        'get_random_cols': [
            ('apply_transforms', [transforms]),
            ('set_dtypes', [index]),
            ('get_random_cols', [5])
        ],
        'get_random_stats': [
            ('apply_transforms', [transforms]),
            ('set_dtypes', [index]),
            ('get_random_stats', [index, 5])
        ],
        'check_output': [  # for sanity checks
            ('apply_index', [index]),
            ('apply_transforms', [transforms]),
            ('check_output', [transforms]),
        ]
    }
    run_benchmark(lib, dataset, benchmarks[args.benchmark])
