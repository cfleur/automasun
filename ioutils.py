import h5py
import pandas as pd
import numpy as np
import os
from pathlib import Path


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


def parse_pressure_file(
        input_file_path: str, 
        output_file_path: str, 
        pressure_correction: None = None,
        in_sep: str ='\s\s+',
        out_sep: str ='\t', 
        in_col_names: None = None, 
        out_col_names: None = None) -> None:
    """Takes aws .lst file as input and creates a .csv file with data necessary for retrieval algorithm. Pre
    """

    df = pd.read_csv(input_file_path, sep=in_sep, engine='python').drop(0)

    # separate date and time from timestamp
    # note that date and time are strings
    _date = []
    _time = []

    # set default values for mutable types 
    if in_col_names == None:
        in_col_names = {}
    
    if out_col_names == None:
        out_col_names = {
            'date': 'UTCdate', 
            'time': 'UTCtime', 
            'pressure': 'BaroTHB40'
        }

    # parse timestamp
    if 'timestamp_col_name' in in_col_names: 
        timestamp_col_name = in_col_names['timestamp_col_name']
    else: 
        timestamp_col_name = df.columns[0]

    for row in df[timestamp_col_name]:
        row_items = row.split(' ')
        _date.append(str(row_items[0]))
        _time.append(str(row_items[1]))

    # apply correction to pressure column if correction provided
    _pressure = df['P_ST']

    if pressure_correction == None:
        print('No pressure correction applied.')
    elif type(pressure_correction) == float:
        _pressure += pressure_correction # subtract the pressure_correction from each measurement if offest is a scalar
        print(f'Scalar pressure offest of {pressure_correction:.5f} applied.')
    elif len(pressure_correction) == len(_pressure):
        _pressure += pressure_correction # subtract the pressure_correction vector from the pressure measurement vector if pressure_correction is a vector
        print('Vector pressure correction applied.')
    else:
        raise ValueError('Pressure correction must be either None (default), a float, or a numpy array of floats of same length as number of pressure measurements.')

    # create new dataframe
    _out_pressure = pd.DataFrame(np.array([_date, _time, _pressure]).T, columns=[out_col_names['date'], out_col_names['time'], out_col_names['pressure']])
    
    # export
    _out_pressure.to_csv(output_file_path, index=False, sep=out_sep)

    print(f'{output_file_path} pressure file written.')


def preprocess_pressure_file(input_pressure_file: str, 
                             out_dir_name: str,
                             out_file_name: str,
                             pressure_correction: any) -> None:

    # create directories needed in output file path
    Path(out_dir_name).mkdir(parents=True, exist_ok=True)

    out_f = os.path.join(out_dir_name, out_file_name)

    parse_pressure_file(input_pressure_file, out_f, pressure_correction=pressure_correction)
