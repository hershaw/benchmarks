from util import timer
from index import index
from transforms import transforms
import sys


def run_benchmark(libname, filename, benchmarks):
    if libname == 'pandas':
        import pandas_benchmark as module
    elif libname == 'sframe':
        import sframe_benchmark as module

    timer.start('{}-load_csv'.format(libname))
    frame = module.load_csv('../data/{}.csv'.format(filename))
    timer.end('{}-load_csv'.format(libname))

    timer.start('{}-total'.format(libname))
    for funcname, args in benchmarks:
        timer.start('{}-{}'.format(libname, funcname))
        frame = getattr(module, funcname)(frame, *args)
        timer.end('{}-{}'.format(libname, funcname))
    timer.end('{}-total'.format(libname))


if __name__ == '__main__':
    run_benchmark(sys.argv[1], sys.argv[2], [
        ('apply_index', [index]),
        ('apply_transforms', [transforms]),
        ('calculate_stats', [index]),
        ('check_output', [transforms]),
    ])
