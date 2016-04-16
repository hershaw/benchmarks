import sframe
from util import force_float, split_drops_combines
import datetime as dt


def to_datetime(val):
    try:
        return dt.datetime.strptime(val, '%b-%Y')
    except:
        return None


def apply_index(sf, index):
    for col in index:
        sarr = sf[col['name']]
        if col['type'] == 'date':
            sf[col['name']] = sarr.apply(to_datetime)
        elif col['type'] == 'number':
            sf[col['name']] = sarr.apply(force_float)
        # elif col['type'] == 'category':
            # sf[col['name']] = sarr.apply(empty_str_to_null)
    # make sure all transforms are applied
    len(sf)
    return sf


def sarr_to_list(sarr):
    return map(lambda x: x, sarr)


def num_uniques(sf, col):
    uniques = sarr_to_list(sf.groupby(col, sframe.aggregate.COUNT))
    return uniques


def load_csv(pathname):
    return sframe.SFrame.read_csv(pathname)


def do_drops(sf, drops):
    for drop in drops:
        payload = set(drop['payload'])
        sf = sf[sf[drop['name']].apply(lambda x: x not in payload)]
    # make sure all transforms are applied
    len(sf)
    return sf


def do_combines(sf, combines):
    for c in combines:
        newval = '_'.join(map(str, c['payload']))
        c['payload'] = set(c['payload'])
        sf[c['name']] = sf[c['name']].apply(
            lambda x: newval if x in c['payload'] else x)
    # make sure all transforms are applied
    len(sf)
    return sf


def apply_transforms(sf, transforms):
    drops, combines = split_drops_combines(transforms)
    sf = do_drops(sf, drops)
    do_combines(sf, combines)
    len(sf)
    return sf


def calculate_stats(sf, index):
    info = []
    for col in index:
        name, _type = col['name'], col['type']
        if _type == 'number':
            info.append(sf.groupby(name, {
                'min': sframe.aggregate.MIN(name),
                'max': sframe.aggregate.MAX(name),
                'mean': sframe.aggregate.MEAN(name),
            }))
        elif _type == 'category':
            info.append(sf.groupby(name, {
                'uniques': sframe.aggregate.COUNT_DISTINCT(name),
                'counts': sframe.aggregate.FREQ_COUNT(name),
            }))
        # make sure it's actually applied
        len(info[-1])
    return sf


def check_output(sf, transforms):
    for tform in transforms:
        uniq = set([x for x in sf[tform['name']].unique()])
        payload = set(tform['payload'])
        assert not uniq & payload, payload


# little optimization yucheng told me to do
sframe.SArray([1, 2, 3]).apply(lambda x: x+1)
