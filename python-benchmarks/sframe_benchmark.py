from collections import Counter
import sframe
from util import force_float, split_drops_combines
import datetime as dt


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


def calculate_stats(sf, index):
    info = []
    for col in index:
        name, _type = col['name'], col['type']
        sarr = sf[name]
        if _type in ('number', 'date'):
            info.append({
                'min': sarr.min(),
                'max': sarr.max(),
                'mean': sarr.mean(),
            })
        elif _type == 'category':
            uniqCounts = Counter()

            def inc(x): uniqCounts[x] += 1
            sarr.apply(inc)

            info.append({
                'uniques': len(uniqCounts),
                'counts': uniqCounts.most_common(10),
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
