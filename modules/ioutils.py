import shutil
import yaml
from datetime import datetime, date as Date
from pathlib import Path, PosixPath
from typing import Union, List

import h5py
import pandas as pd

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


def create_file_path(
        dir_path: Union[str, PosixPath],
        file_name: str,
) -> PosixPath:
    dir = Path(dir_path)
    dir.mkdir(parents=True, exist_ok=True)
    return dir/file_name


def get_file_extension(
        file_path_or_name: Union[str, PosixPath],
        v: bool = False
) -> str:
    extension = str(file_path_or_name).rsplit(sep='.', maxsplit=1)[-1]
    if v == True:
        print(f'File extension: {extension}')
    return extension


def read_yaml_config(
        config_file_path: Union[str, PosixPath]
) -> dict:
    with open(config_file_path, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


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


def read_file_names(
        folder_path: Union[str, PosixPath],
        v: bool = False
) -> List[str]:
    """
    Returns a list of names of files in a folder.
    """
    if v:
        print(f'Reading file names from {folder_path}')
    file_names = [
        file.name for file in Path(folder_path).glob('*')
        if not file.is_dir()
    ]
    if v:
        print(file_names)
    return file_names


def extract_date_from_fname(
        file_name: str
) -> Date:
    """
    Parses a date from a filename.

    Note: custom parsing instead of datetime's strptime for more
    flexibility in file names.
    """
    file_type = get_file_extension(file_name)
    if file_type == 'lst':
        # aws_yyyymmdd.lst
        date_string = file_name.split('.')[0].split('_')[1]
        year = date_string[0:4]
        month = date_string[4:6]
        day = date_string[6:8]
    elif file_type == 'txt':
        # yymmdd_PTU300_log.txt or yymmdd_PTU300_error_log.txt
        date_string = file_name.split('.')[0].split('_')[0]
        year = '20' + date_string[0:2]
        month = date_string[2:4]
        day = date_string[4:6]
    elif file_type == 'csv':
        # prefix-<location>-yyyymmdd.csv
        date_string = file_name.split('.')[0].split('-')[2]
        year = date_string[0:4]
        month = date_string[4:6]
        day = date_string[6:8]
    else:
        raise TypeError(
            f'Pressure file type \'{file_type}\' not supported.'
            ' Supported types: .lst, .txt, .csv'
        )
    date = datetime(int(year), int(month), int(day)).date()
    return date


def generate_fname_from_date(
        date: Date,
        file_type: str,
        location: Union[str, None] = None,
        v: bool = False
) -> str:
    """
    Generates a filename from a date
    """
    if file_type == 'lst':
        # aws_yyyymmdd.lst
        date_string = date.strftime("%Y%m%d")
        file_name = f'aws_{date_string}.lst'
    elif file_type == 'txt':
        # yymmdd_PTU300_log.txt
        date_string = date.strftime("%y%m%d")
        file_name = f'{date_string}_PTU300_log.txt'
    elif file_type == 'csv':
        # prefix-<location>-yyyymmdd.csv
        date_string = date.strftime("%Y%m%d")
        if location is not None:
            file_name = f'pressure-{location}-{date_string}.csv'
        else:
            raise ValueError(
                'Sensor location value needed for generating csv file name.'
            )
    else:
        raise TypeError(
            f'Pressure file type \'{file_type}\' not supported.'
            ' Supported types: .lst, .txt, .csv'
        )
    if v:
        print(
            f'file name from date: {file_name}'
        )
    return file_name


def generate_file_list(
        date_list: Union[list, set],
        file_type: str,
        location: Union[str, None] = None,
        v: bool = False,
) -> List[str]:
    """
    Generates a list of file names from a list of dates
    for a given file type.
    """
    if isinstance(date_list, set):
        date_list = list(date_list)
    elif isinstance(date_list, list):
        pass
    else:
        raise TypeError(
            f'date_list was {type(date_list)} but must be list or set type.'
        )
    file_list = []
    for d in date_list:
        file_list.append(
            generate_fname_from_date(
                d, file_type, location=location, v=v
            )
        )
    return sorted(file_list)


def generate_date_list(
        folder_path: Union[str, PosixPath],
        start_date: Date,
        end_date: Date,
        v: bool = False,
        vv: bool = False
) -> List[Date]:
    """
    Generates a list of date objects from a folder containing
    file names that include the date.
    """
    file_names = read_file_names(folder_path, v=v)
    date_list = []
    for f in file_names:
        try:
            d = extract_date_from_fname(f)
            if timeutils.date_in_range(
                d, start_date=start_date, end_date=end_date
            ):
                date_list.append(d)
            if vv:
                print(f'file\'{f}\': {d} date extracted.')
        except Exception as e:
            if v:
                print(f'* file\'{f}\': {e}')
    return sorted(date_list)


def generate_set_difference(
        s1: set,
        s2: set
) -> set:
    """
    Returns the elements that are in s1 and not in s2.
    s1 might be a raw data folder and s2 might be a processed data folder.
    """
    return s1.difference(s2)
