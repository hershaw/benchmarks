import os
import argparse
from statistics import mean
# import os
from util import timer
from index import index
from transforms import transforms


parser = argparse.ArgumentParser()
parser.add_argument(
    '-l', '--lib',
    help='Library to use.', type=str, choices=['pandas', 'sframe'],
    required=True)
parser.add_argument(
    '-d', '--dataset', help='Which dataset to use', type=str, required=True)
parser.add_argument(
    '-t', '--transforms', help='Which set of transforms to run', type=str,
    choices=['small', 'medium', 'large'], required=False)
parser.add_argument(
    '-f', '--stats-for', help='Which column to get stats for', type=str,
    required=False)
parser.add_argument(
    '-b', '--benchmark', help='Which benchmark to use.', type=str,
    choices=['apply_index_and_write', 'get_random_cols',
             'get_random_stats', 'print_stats_for'],
    required=True)
parser.add_argument(
    '-n', '--nruns', help='How many times to run the benchmark', type=int,
    default=1)


args = parser.parse_args()


def realpath(fname):
    return './data/{}.csv'.format(fname)


def get_module(libname):
    if libname == 'pandas':
        import pandas_benchmark as module
    elif libname == 'sframe':
        import sframe_benchmark as module
    else:
        raise ValueError('no lib with name "{}" found'.format(libname))
    return module


def run_benchmark(libname, frame, benchmarks):
    module = get_module(libname)
    frame = module.copy_frame(frame)

    timer.start('{}-total'.format(libname))
    for funcname, args in benchmarks:
        timer.start('{}-{}'.format(libname, funcname))
        frame = getattr(module, funcname)(frame, *args)
        timer.end('{}-{}'.format(libname, funcname))

    print('+++++++++++++++++++++++++++++++')
    totaltime = timer.end('{}-total'.format(libname))
    print('+++++++++++++++++++++++++++++++')
    return totaltime


def start_memory_profiling():
    name = benchmark_name()
    pid = os.getpid()
    os.system('nohup pidstat -r -p {} > profile/`hostname`-{}.mem &'.format(
                pid, name))


def benchmark_name():
    return '{}-{}-{}-{}'.format(
        args.lib, args.dataset, args.benchmark, args.transforms)


if __name__ == '__main__':
    libname = args.lib
    dataset = args.dataset
    benchmark = args.benchmark
    transforms = transforms[args.transforms] if args.transforms else None
    if args.benchmark != 'apply_index_and_write' and transforms is None:
        raise ValueError('transforms required for {}'.format(args.benchmark))
    benchmarks = {
        'apply_index_and_write': [
            ('apply_index', [index]),
            ('to_file', [realpath('{}_{}'.format(libname, dataset))]),
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
        # for quick visual inspection
        'print_stats_for': [
            ('apply_transforms', [transforms]),
            ('set_dtypes', [index]),
            ('print_stats_for', [index, args.stats_for])
        ],
        'check_output': [  # for sanity checks
            ('apply_index', [index]),
            ('apply_transforms', [transforms]),
            ('check_output', [transforms]),
        ]
    }
    module = get_module(libname)
    timer.start('{}-load'.format(libname))
    frame = module.load_file(realpath(dataset))
    timer.end('{}-load'.format(libname))

    start_memory_profiling()

    times = []
    for i in range(0, args.nruns):
        times.append(
            run_benchmark(libname, frame, benchmarks[args.benchmark]))

    print('\n'.join(map(str, times)))
    print('Average time: {}'.format(mean(times)))
    withavg = times + [mean(times)]
    os.system('echo "%s" > timings/%s' % (
        '\n'.join(map(str, withavg)), benchmark_name()))
