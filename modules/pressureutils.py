import pandas as pd
import numpy as np

from typing import Union, List
from pathlib import PosixPath, Path
from datetime import datetime, timedelta
from . import timeutils
from . import ioutils


def parse_pressure_file(
        input_file_path: Union[str, PosixPath],
        output_file_path: Union[str, PosixPath],
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
        print('*'*4,'Creating formatted pressure file.')
    # set default values for mutable type arguments
    if in_col_names is None:
        in_col_names = {}
    if out_col_names is None:
        out_col_names = {
            'date': 'UTCdate',
            'time': 'UTCtime',
            'pressure': 'BaroTHB40'
        }
    #TODO: use function get_file_extension
    input_file_type = str(input_file_path).split(sep='.')[-1]
    if input_file_type == 'lst':
        if in_sep is None:
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
        if in_sep is None:
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
    _out_pressure.to_csv(output_file_path, index=False, sep=out_sep)
    if not q:
        print(f'{output_file_path.name} pressure file written {datetime.now().time()}.')
    if v:
        print(f'Pressure file location: {output_file_path}')


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

import importlib
importlib.reload(ioutils)

def generate_unparsed_pressure_file_list(
        instrument: str,
        location: str,
        config_file: Union[str, PosixPath],
        v: bool = False,
        vv: bool = False
) -> List[Union[str, PosixPath]]:
    """
    Takes raw and parsed pressure folders from a config file and
    compares the contents based on dates in the file names.
    Returns a list of unparsed pressure files.
    """
    config = ioutils.read_yaml_config(config_file)
    raw_pressure_folder = config[instrument][location]['raw_pressure_folder']
    parsed_pressure_folder = config[instrument][location]['parsed_pressure_folder']
    start_date = datetime.strptime(
        config[instrument][location]['start_date'],
        "%Y-%m-%d"
    ).date()
    if config[instrument][location]['end_date'] is None:
        end_date = datetime.now().date() - timedelta(days=1)
    else:
        end_date = datetime.strptime(
            config[instrument][location]['end_date'],
            "%Y-%m-%d"
    ).date()
    raw_pressure_dates = ioutils.generate_date_list(
        raw_pressure_folder,
        start_date=start_date,
        end_date=end_date,
        v=v,
        vv=vv
    )
    parsed_pressure_dates = ioutils.generate_date_list(
        parsed_pressure_folder,
        start_date=start_date,
        end_date=end_date,
        v=v,
        vv=vv
    )
    unparsed_pressure_dates = ioutils.generate_set_difference(
        set(raw_pressure_dates),
        set(parsed_pressure_dates)
    )
    unparsed_pressure_files = ioutils.generate_file_list(
        unparsed_pressure_dates,
        'txt'
    )
    output_file_names = ioutils.generate_file_list(
        unparsed_pressure_dates,
        'csv',
        location
    )
    unparsed_pressure_paths = [
        Path(raw_pressure_folder)/file
        for file
        in unparsed_pressure_files
    ]
    output_paths = [
        Path(parsed_pressure_folder)/name
        for name
        in output_file_names
    ]
    return unparsed_pressure_paths, output_paths
