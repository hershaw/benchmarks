import pandas as pd
from util import split_drops_combines, force_float


def load_csv(filename):
    return pd.read_csv(filename)


def apply_index(df, index):
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


def drop_rows_with_vals(df, drops):
    for drop in drops:
        if len(drop['payload']) == 0:
            return
        colname = drop['name']
        df.drop(df[colname].isin(drop['payload']), inplace=True)


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


def calculate_stats(df, index):
    info = []
    for col in index:
        name, _type = col['name'], col['type']
        series = df[name]
        if _type == 'number':
            info.append({
                'min': series.min(),
                'max': series.max(),
                'mean': series.mean(),
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
