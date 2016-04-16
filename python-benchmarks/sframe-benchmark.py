import sframe
# import datetime as dt
# import re
from transforms import transforms
from util import timer, split_drops_combines


"""

strip_non_number_regex = re.compile('[^0-9\.,]')

def to_datetime(val):
    try:
        return dt.datetime.strptime(val, '%b-%Y')
    except:
        return None


def force_float(x):
    try:
        return float(x)
    except:
        try:
            return float(
                strip_non_number_regex.sub('', x).replace(',', '.'))
        except:
            return None


def empty_str_to_null(x):
    if x == '':
        return None
    return x


def apply_index(sf, index):
    for col in index:
        sarr = sf[col['name']]
        if col['type'] == 'date':
            sf[col['name']] = sarr.apply(to_datetime)
        elif col['type'] == 'number':
            sf[col['name']] = sarr.apply(force_float)
        elif col['type'] == 'category':
            sf[col['name']] = sarr.apply(empty_str_to_null)


def sarr_to_list(sarr):
    return map(lambda x: x, sarr)

def num_uniques(sf, col):
    uniques = sarr_to_list(sf.groupby(col, sframe.aggregate.COUNT))
    return uniques
"""


def read_csv(pathname):
    return sframe.SFrame.read_csv(pathname)


def do_drops(sf, drops):
    for drop in drops:
        drop['payload'] = set(drop['payload'])
        sf = sf[sf[drop['name']].apply(lambda x: x not in drop['payload'])]
    return sf


def do_combines(sf, combines):
    for c in combines:
        newval = '_'.join(map(str, c['payload']))
        c['payload'] = set(c['payload'])
        sf[c['name']] = sf[c['name']].apply(
            lambda x: newval if x in c['payload'] else x)


def apply_transforms(sf, transforms):
    drops, combines = split_drops_combines(transforms)
    sf = do_drops(sf, drops)
    do_combines(sf, combines)
    len(sf)
    return sf


def check_output(sf):
    for tform in transforms:
        uniq = set([x for x in sf[tform['name']].unique()])
        payload = set(tform['payload'])
        assert not uniq & payload, payload


def main():

    sframe.SArray([1, 2, 3]).apply(lambda x: x+1)
    timer.start('sframe read csv')
    sf = read_csv('./data/lc_big.csv')
    timer.end('sframe read csv')
    timer.start('sframe apply transforms')
    sf = apply_transforms(sf, transforms)
    timer.end('sframe apply transforms')
    check_output(sf)


if __name__ == '__main__':
    main()
