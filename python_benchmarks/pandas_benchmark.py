import random
from functools import reduce
import pandas as pd
# import numpy as np
from util import split_drops_combines, force_float, pretty_print


def load_file(filename):
    return pd.read_csv(filename)


def to_file(df, filename):
    df.to_csv(filename, index=False, encoding='utf-8')
    return df


def copy_frame(df):
    return pd.DataFrame(df)


def remove_columns(df, index):
    index_names = set(list(map(lambda x: x['name'], index)))
    column_names = set(df.columns)
    diff = column_names - index_names
    if len(diff):
        for colname in diff:
            df.drop(colname, axis=1, inplace=True)


def apply_index(df, index):
    remove_columns(df, index)
    for col in index:
        name, _type = col['name'], col['type']
        series = df[name]
        if _type == 'date':
            df[name] = pd.to_datetime(series, errors='coerce', format='%m-%Y')
        elif _type == 'number':
            df[name] = series.map(force_float)
    return df


def set_dtypes(df, index):
    # I don't think anything needs to be done here...
    return df


def drop_rows_with_vals(df, drops):
    for drop in drops:
        if len(drop['payload']) == 0:
            continue
        payload = drop['payload']
        colname = drop['name']
        mask = df[colname].isin(payload)
        df.drop(df.loc[mask].index, inplace=True)


def combine(df, combines):
    for c in combines:
        colname, payload = c['name'], c['payload']
        payload.sort()
        repwith = '%s_%s' % (
            colname, '-'.join([str(val) for val in payload[:2]]))
        payload = {val: repwith for val in payload}
        df[colname] = df[colname].map(payload)


def apply_transforms(df, transforms):
    drops, combines = split_drops_combines(transforms)
    drop_rows_with_vals(df, drops)
    combine(df, combines)
    return df


def get_random_cols(df, ncols):
    colnames = df.columns
    coldata = []
    for i in range(0, ncols):
        colname = random.choice(colnames)
        coldata.append(list(df[colname]))
    return coldata


def get_hist(series, nbins, _min, _max):
    if _min == _max or not len(series):
        return [len(series)]

    binned, cuts = pd.cut(
        series, nbins, retbins=True, labels=list(range(0, nbins)))

    bins = []
    for i, c in enumerate(cuts[0:-1]):
        bins.append({'start': c, 'end': cuts[i + 1], 'count': 0})

    def buildhist(_bins, bin_index):
        bins[bin_index]['count'] += 1
        return _bins

    return reduce(buildhist, binned, bins)


def get_random_stats(df, index, ncols):
    colstats = []
    for i in range(0, ncols):
        col_index = random.randint(0, len(index) - 1)
        col = index[col_index]
        name, _type = col['name'], col['type']
        colstats.append(calculate_col_stats(df[name], name, _type))
    return colstats


def print_stats_for(df, index, colname):
    col = list(filter(lambda x: x['name'] == colname, index))[0]
    name, _type = col['name'], col['type']
    stats = calculate_col_stats(df[name], name, _type)
    pretty_print(stats)
    return stats


def calculate_col_stats(series, name, _type):
    if _type in ('number', 'date'):
        series = series.dropna()
        _min, _max = series.min(), series.max()
        return {
            'min': _min,
            'max': _max,
            'mean': series.mean(),
            'hist': get_hist(series, 30, _min, _max),
            'name': name,
        }
    elif _type == 'category':
        return {
            'uniques': series.nunique(),
            'counts': series.value_counts(),
            'name': name,
        }


def calculate_stats(df, index):
    info = []
    for col in index:
        name, _type = col['name'], col['type']
        info.append(calculate_col_stats(df[name], name, _type))
    return df


def check_output(df, transforms):
    for tform in transforms:
        assert not df[tform['name']].isin(tform['payload']).sum()
    return df
