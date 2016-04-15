import pandas as pd
from transforms import transforms
from util import split_drops_combines, timer

"""
Begin pandas code
"""


def pandas_drop_rows_with_vals(df, drops):
    for drop in drops:
        if len(drop['payload']) == 0:
            return
        colname = drop['name']
        df.drop(df[colname].isin(drop['payload']), inplace=True)


def pandas_combine(df, combines):
    timer.start('combines')
    for c in combines:
        colname = c['name']
        values = c['payload']
        values.sort()
        repwith = '%s_%s' % (
            colname, '-'.join([str(val) for val in values[:2]]))
        values = {val: repwith for val in values}
        df[colname] = df[colname].map(values)
    timer.end('combines')


def pandas_apply_transforms(df, transforms):
    timer.start('transforms')
    drops, combines = split_drops_combines(transforms)
    pandas_drop_rows_with_vals(df, drops)
    pandas_combine(df, combines)
    timer.end('transforms')


def main():
    timer.start('pandas read csv')
    df = pd.read_csv('./data/lc_big.csv')
    timer.end('pandas read csv')
    timer.start('pandas apply transforms')
    pandas_apply_transforms(df, transforms)
    timer.end('pandas apply transforms')

if __name__ == '__main__':
    main()
