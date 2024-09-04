import h5py
import pandas as pd
import numpy as np
import shutil

from pathlib import Path
from datetime import datetime
from typing import Union

from . import timeutils


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


def preprocess_pressure_file(
        input_pressure_file: str,
        out_dir_name: str,
        out_file_name: str,
        pressure_correction: Union[None, float, list] = None,
        in_sep: Union[None, str] = None,
        v: bool = False
) -> None:
    input_file_type = str(input_pressure_file).split(sep='.')[-1]

    # create directories needed in output file path
    out_dir = Path(out_dir_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir/out_file_name

    parse_pressure_file(
        input_pressure_file,
        input_file_type,
        out_file,
        pressure_correction=pressure_correction,
        in_sep=in_sep,
        v=v
    )


def parse_pressure_file(
        input_file_path: str, 
        input_file_type: str,
        output_file_path: str, 
        pressure_correction: Union[None, float, list] = None,
        in_sep: Union[None, str] = None,
        out_sep: str ='\t', 
        in_col_names: Union[None, dict] = None,
        out_col_names: Union[None, dict] = None,
        v: bool = False,
        q: bool = False
) -> None:
    """Takes aws .lst or txt log pressure file as input and
    creates a .csv file with data necessary for retrieval algorithm.
    """
    if v:
        print('Creating formatted pressure file.')
    # set default values for mutable type arguments 
    if in_col_names == None:
        in_col_names = {}
    if out_col_names == None:
        out_col_names = {
            'date': 'UTCdate', 
            'time': 'UTCtime', 
            'pressure': 'BaroTHB40'
        }
    
    if input_file_type == 'lst':
        if in_sep == None:
            in_sep = '\s\s+'
        df = pd.read_csv(input_file_path, sep=in_sep, engine='python').drop(0)

        # parse timestamp
        if 'timestamp_col_name' in in_col_names:
            timestamp_col_name = in_col_names['timestamp_col_name']
        else:
            timestamp_col_name = df.columns[0]
        timestamps = list(df[timestamp_col_name])
        timestamp_df = timeutils.timestamp_to_date_time(timestamps)

        _pressure = df['P_ST']
        _out_pressure = pd.DataFrame(
            np.array([
                timestamp_df['date'],
                timestamp_df['time'],
                apply_pressure_correction(_pressure, pressure_correction, q)
            ]).T,
            columns=[
                out_col_names['date'],
                out_col_names['time'],
                out_col_names['pressure']
            ])
    elif input_file_type == 'txt':
        if in_sep == None:
            in_sep = '\s+'
        df = pd.read_csv(input_file_path, sep=in_sep, engine='python', skiprows=2, header=None)
        _pressure = df[9]
        _out_pressure = pd.DataFrame(
            np.array([
                df[0],
                df[1],
                apply_pressure_correction(_pressure, pressure_correction, q),
                df[12],
                df[15]
            ]).T,
            columns=[
                out_col_names['date'],
                out_col_names['time'],
                out_col_names['pressure'],
                'TemperatureC',
                'RelativeHumidity'
            ])
    else:
        raise ValueError(
            f'Supported input file types: .lst, .txt.'
            f' Got {input_file_type}.'
        )

    # export
    out_file = Path(output_file_path)
    _out_pressure.to_csv(out_file, index=False, sep=out_sep)

    if not q:
        print(f'{out_file.name} pressure file written {datetime.now().time()}.')
    if v:
        print(f'Pressure file location: {out_file}')


def apply_pressure_correction(
        pressure_vector: pd.Series,
        pressure_correction: Union[None, float, list] = None,
        q: bool = False
) -> pd.Series:
    if pressure_correction == None:
        if not q:
            print('No pressure correction applied.')
    elif type(pressure_correction) == float:
        # subtract the pressure_correction
        # from each measurement if offest is a scalar
        pressure_vector += pressure_correction
        if not q:
            print(f'Scalar pressure offest of {pressure_correction:.5f} applied.')
    else:
        try:
            len(pressure_correction) == len(pressure_vector)
            # subtract the pressure_correction vector from the
            # pressure measurement vector if pressure_correction is a vector
            pressure_vector += pressure_correction
            if not q:
                print('Vector pressure correction applied.')
        except:
            raise ValueError(
                'Pressure correction must be either None (default), a float,'
                ' or an array of floats of same length as number of pressure measurements.'
            )
    return pressure_vector


def filter_move_files(
        src_path: str,
        glob_pattern: str,
        dest_path: str,
        quiet: bool = False
) -> None:
    """
    Filters files by `file_extension` and moves all files of same extension to 
    `dest_path`. 
    """

    src = Path(src_path)

    if not quiet:
        print(f'Searching for pattern {glob_pattern} in {src}')

    glob_contents = list(src.glob(glob_pattern))

    if not quiet:
        print(f'Creating directory {dest_path} if doesn\'t exist')

    Path(dest_path).mkdir(parents=True, exist_ok=True)
    # TODO: test that the directory was created

    file_count = 0

    for file in glob_contents:
        file_count += 1
        shutil.move(file, dest_path)

    print(f'Moved {file_count} files matching pattern {glob_pattern}')
    

def separate_mod_vmr_map(
        src_path: str,
        dest_dict: dict,
) -> None:
    """
    Moves all files of a given extension (e.g. `*.mod`, `.*vmr`, `*.mod`) from a src folder to specified destinations.
    `dest_dict` keys should be formatted as `.<file_extension>` and values should be destination path.
    """

    for ext, dest in zip(dest_dict.keys(), dest_dict.values()):
        glob_pattern = f'*{ext}'
        filter_move_files(src_path, glob_pattern, dest)       

    