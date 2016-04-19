import pandas as pd
# import numpy as np
from util import split_drops_combines, force_float


def load_file(filename):
    if filename.endswith('.csv'):
        return pd.read_csv(filename)
    elif filename.endswith('.json'):
        return pd.read_json(filename)


def to_file(df, filename, _format):
    if _format == 'csv':
        df.to_csv(filename, index=False, encoding='utf-8')
    elif _format == 'json':
        df.to_json(filename)
    return df


def remove_columns(df, index):
    index_names = set(list(map(lambda x: x['name'], index)))
    column_names = set(df.columns)
    diff = column_names - index_names
    if len(diff):
        print('removing {} columns'.format(len(diff)))
        for colname in diff:
            df = df.drop(colname, axis=1, inplace=True)
    return df


def apply_index(df, index):
    df = remove_columns(df, index)
    for col in index:
        series = df[col['name']]
        if col['type'] == 'date':
            df[col['name']] = pd.to_datetime(
                series, errors='coerce', format='%m-%Y')
        elif col['type'] == 'number':
            df[col['name']] = series.map(force_float)
        # elif col['type'] == 'category':
            # sf[col['name']] = sarr.apply(empty_str_to_null)
    return df


def set_dtypes(df, index):
    # I don't think anything needs to be done here...
    return df


def drop_rows_with_vals(df, drops):
    for drop in drops:
        if len(drop['payload']) == 0:
            return
        payload = set(drop['payload'])
        colname = drop['name']
        # need to check if the payload exists or pandas will throw an exception
        mask = df[colname].isin(payload)
        df.drop(df.loc[mask].index, inplace=True)


def combine(df, combines):
    for c in combines:
        colname = c['name']
        values = c['payload']
        values.sort()
        repwith = '%s_%s' % (
            colname, '-'.join([str(val) for val in values[:2]]))
        values = {val: repwith for val in values}
        df[colname] = df[colname].map(values)


def apply_transforms(df, transforms):
    drops, combines = split_drops_combines(transforms)
    drop_rows_with_vals(df, drops)
    combine(df, combines)
    return df


def get_hist(series, nbins, _min, _max):
    if _min == _max or not len(series):
        return [len(series)]
    # not the same format as the sframe one, but this should be okay
    return pd.cut(series, nbins)


def calculate_stats(df, index):
    info = []
    for col in index:
        name, _type = col['name'], col['type']
        series = df[name]
        if _type == 'number':
            series = series.dropna()
            _min, _max = series.min(), series.max()
            info.append({
                'min': _min,
                'max': _max,
                'mean': series.mean(),
                'hist': get_hist(series, 30, _min, _max)
            })
        elif _type == 'category':
            info.append({
                'uniques': series.nunique(),
                'counts': series.value_counts(),
            })
    return df


def check_output(df, transforms):
    for tform in transforms:
        assert not df[tform['name']].isin(tform['payload']).sum()
    return df
