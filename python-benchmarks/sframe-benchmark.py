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


def create_drops_filter(drops):
    for drop in drops:
        drop['payload'] = set(drop['payload'])

    def real_drop(x):
        for drop in drops:
            if x[drop['name']] in drop['payload']:
                return False
        return True
    return real_drop


def apply_combines(sf, combines):

    def create_combine_func(vals, newval):
        def real_combine(x):
            if x in vals:
                return newval
            return x
        return real_combine

    for c in combines:
        newval = '_'.join(map(str, c['payload']))
        func = create_combine_func(set(c['payload']), newval)
        sf[c['name']] = sf[c['name']].apply(func)


def apply_transforms(sf, transforms):
    # first do all drops
    drops, combines = split_drops_combines(transforms)
    # this will create a copy
    sf = sf[sf.apply(create_drops_filter(drops))]
    # this will make the changes in place
    apply_combines(sf, combines)
    return sf


def main():
    timer.start('sframe read csv')
    sf = read_csv('./data/lc_big.csv')
    timer.end('sframe read csv')
    timer.start('sframe apply transforms')
    apply_transforms(sf, transforms)
    timer.end('sframe apply transforms')


if __name__ == '__main__':
    main()
