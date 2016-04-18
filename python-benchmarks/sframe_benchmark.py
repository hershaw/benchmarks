from collections import Counter
import sframe
from util import force_float, split_drops_combines
import datetime as dt
import math


def to_datetime(val):
    try:
        return (
            dt.datetime.strptime(val, '%b-%Y') - dt.datetime(1970, 1, 1)).total_seconds() * 1000
    except:
        return None


def apply_index(sf, index):
    for col in index:
        name, _type = col['name'], col['type']
        if _type == 'date':
            sf[name] = sf[name].apply(to_datetime).astype(int)
        elif _type == 'number':
            sf[name] = sf[name].apply(force_float).astype(float)
        # I don't think you need to set category as a type. all the stats
        # we care about should continue to work.
    return sf


def set_dtypes(sf, index):
    for col in index:
        name, _type = col['name'], col['type']
        if _type == 'date':
            sf[name] = sf[name].astype(int)
        elif _type == 'number':
            sf[name] = sf[name].astype(float)
    return sf


def sarr_to_list(sarr):
    return map(lambda x: x, sarr)


def num_uniques(sf, col):
    uniques = sarr_to_list(sf.groupby(col, sframe.aggregate.COUNT))
    return uniques


def load_csv(filename):
    return sframe.SFrame.read_csv(filename)


def to_csv(sf, filename):
    sf.save(filename, 'csv')
    return load_csv(filename)


def do_drops(sf, drops):
    for drop in drops:
        payload = set(drop['payload'])
        sf = sf[sf[drop['name']].apply(lambda x: x not in payload)]
    return sf


def do_combines(sf, combines):
    for c in combines:
        newval = '_'.join(map(str, c['payload']))
        payload = set(c['payload'])
        sf[c['name']] = sf[c['name']].apply(
            lambda x: newval if x in payload else x)
    return sf


def apply_transforms(sf, transforms):
    drops, combines = split_drops_combines(transforms)
    sf = do_drops(sf, drops)
    do_combines(sf, combines)
    return sf


def get_hist(sarr, nbins, _min, _max):
    # assuming the sarr is already sorted

    if _min == _max:
        return [{'start': _min, 'end': _max, 'count': len(sarr)}]

    bins = []
    step_size = (_max - _min) / nbins
    i = _min
    while i < _max:
        bins.append({'start': i, 'end': min(i + step_size, _max), 'count': 0})
        i += step_size

    def incbin(index_and_bins, x):
        i, _bins = index_and_bins
        if x > _bins[i]['end']:
            i += 1
        _bins[i]['count'] += 1
        return i, _bins

    reduce(incbin, sarr, (0, bins))

"""
def get_hist(sarr, nbins, _min, _max):
    if _min == _max:
        return [{'start': _min, 'end': _max, 'count': len(sarr)}]

    bins = []
    step_size = (_max - _min) / nbins
    i = _min
    while i < _max:
        bins.append({'start': i, 'end': min(i + step_size, _max), 'count': 0})
        i += step_size

    bin_enumerator = list(enumerate(bins))

    def assign_bin(x):
        for i, b in bin_enumerator:
            if x >= b['start'] and x <= b['end']:
                return int(i)
        print('could not bin {}, {}, {}'.format(x, _min, _max))

    bin_assignments = sarr.apply(assign_bin).astype(int)

    def do_bin_count(_bins, i):
        _bins[i]['count'] += 1
        return _bins

    bins = reduce(do_bin_count, bin_assignments, bins)

    return bins
"""


def calculate_stats(sf, index):
    info = []
    for col in index:
        name, _type = col['name'], col['type']
        sarr = sf[name]
        if _type in ('number', 'date'):
            sarr = sarr.dropna().sort()
            _min, _max = sarr.min(), sarr.max()
            info.append({
                'min': _min,
                'max': _max,
                'mean': sarr.mean(),
                'hist': get_hist(sarr, 30, _min, _max)
            })
        elif _type == 'category':

            # do a reduce in order to avoid building a new data structure
            def inc(acc, x):
                acc[x] += 1
                return acc

            counts = reduce(inc, sarr, Counter())
            info.append({
                'uniques': len(counts),
                'counts': counts.most_common(10),
            })
    return sf


def check_output(sf, transforms):
    for tform in transforms:
        uniq = set([x for x in sf[tform['name']].unique()])
        payload = set(tform['payload'])
        assert not uniq & payload, payload
    return sf


# little optimization yucheng told me to do
sframe.SArray([1, 2, 3]).apply(lambda x: x+1)
