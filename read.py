import h5py
import pandas as pd


def h5_get_keys(f):
    with h5py.File(f, 'r') as file:
        return [ k for k in file.keys() ]


def h5_get_col(f, col_num):
    with h5py.File(f, 'r') as file:
        a_group_key = list(file.keys())[col_num]
        return list(file[a_group_key])


def csv_get_keys(f, sep=','):
    df = pd.read_csv(f, sep=sep)
    return df.columns


def csv_get_col(f, col_num, sep=','):
    df = pd.read_csv(f, sep=sep)
    return df[df.columns[col_num]]
