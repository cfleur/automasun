import shutil
import datetime as dt
from pathlib import Path, PosixPath
from typing import List, Union

import yaml

from . import timeutils


##############################################################
################### Working with files #######################
##############################################################

# NOTE: can be used for organising profile files
def separate_mod_vmr_map(
        src_path: str,
        dest_dict: dict,
) -> None:
    """
    Moves all files of a given extension (e.g. `*.mod`, `.*vmr`, `*.mod`) from a src folder to specified destinations.
    `dest_dict` keys should be formatted as `.<file_extension>` and values should be destination path.
    """
    # TODO: generlise naming (does not have to be vmr, mod, map)
    for ext, dest in zip(dest_dict.keys(), dest_dict.values()):
        glob_pattern = f'*{ext}'
        filter_move_files(src_path, glob_pattern, dest)       

# NOTE: can be used for organising profile files
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


def get_file_extension(
        file_path_or_name: Union[str, Path],
        v: bool = False
) -> str:
    """
    Returns the extension part of a file name.
    """
    extension = str(file_path_or_name).rsplit(sep='.', maxsplit=1)[-1]
    if v == True:
        print(f'File extension: {extension}')
    return extension


def read_file_names(
        folder_path: Union[str, PosixPath],
        v: bool = False
) -> List[str]:
    """
    Returns a list of names of files in a folder.
    """
    # TODO: handle case where folder doesn't exits
    # (current behaviour: returns an empty array, folder is created later)
    if v:
        print(f'Reading file names from {folder_path}')
    file_names = [
        file.name for file in Path(folder_path).glob('*')
        if not file.is_dir()
    ]
    if v:
        print(file_names)
    return file_names


##############################################################
############## Working with file name dates ##################
##############################################################


def generate_file_list_from_dates(
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


def generate_fname_from_date(
        date: dt.date,
        file_type: str,
        location: Union[str, None] = None,
        v: bool = False
) -> str:
    """
    Generates a filename from a date
    """
    # TODO: generates from given filename
    # filename format is not hard coded
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
        raise ValueError(
            f'Pressure file type \'{file_type}\' not supported.'
            ' Supported types: .lst, .txt, .csv'
        )
    if v:
        print(
            f'file name from date: {file_name}'
        )
    return file_name


def generate_date_list_from_folder(
        folder_path: Union[str, PosixPath],
        start_date: dt.date,
        end_date: dt.date,
        v: bool = False,
        vv: bool = False
) -> List[dt.date]:
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


def extract_date_from_fname(
        file_name: str
) -> dt.date:
    """
    Parses a date from a filename.

    Note: custom parsing instead of datetime's strptime for more
    flexibility in file names.

    For file type '.lst' file name format is:
        - aws_yyyymmdd.lst

    For file type '.txt' file name format is:
        - yymmdd_PTU300_log.txt or
        - yymmdd_PTU300_error_log.txt
    If string "error" is in name, date will be extracted twice,
    however due to set operations, dates are unique and are only counted once

    For file type '.csv' file name format is:
        - <prefix>-<location>-yyyymmdd.csv
    """
    file_type = get_file_extension(file_name)
    if file_type == 'lst':
        date_string = file_name.split('.')[0].split('_')[1]
        year = date_string[0:4]
        month = date_string[4:6]
        day = date_string[6:8]
    elif file_type == 'txt':
        date_string = file_name.split('.')[0].split('_')[0]
        year = '20' + date_string[0:2]
        month = date_string[2:4]
        day = date_string[4:6]
    elif file_type == 'csv':
        date_string = file_name.split('.')[0].split('-')[2]
        year = date_string[0:4]
        month = date_string[4:6]
        day = date_string[6:8]
    else:
        raise ValueError(
            f'Pressure file type \'{file_type}\' not supported.'
            ' Supported types: .lst, .txt, .csv'
        )
    date = dt.datetime(int(year), int(month), int(day)).date()
    return date


def generate_dirname_from_date(
        date_object: dt.datetime
) -> str:
    """
    Given a datetime object, create a string of the format %Y%m%d.
    """
    try:
        return dt.datetime.strftime(date_object, '%Y%m%d')
    except TypeError:
        print(f'Please provide a valid datetime object. Got {date_object}')
        raise


def extract_date_from_dirname(
        dirname: str
) -> dt.datetime:
    """
    Given a string of format %Y%m%d or %y%m%d returns the date.
    Raises a ValueError for different formats.
    """
    try:
        return dt.datetime.strptime(dirname, '%y%m%d')
        # if the date string has a 2 digit year it will be returned here.
        # it is important to compare evaluate the 2 digit year first
        # because passing a 6 digit string to %Y%m%d will result in incorrect date.
    except ValueError:
        try:
            return dt.datetime.strptime(dirname, '%Y%m%d')
            # if the date has a 4 digit year it will be returned here.
        except ValueError:
            print(f"{dirname} is not in format '%Y%m%d or %y%m%d'.")
            raise


def generate_set_difference(
        s1: set,
        s2: set
) -> set:
    """
    Returns the elements that are in s1 and not in s2.
    s1 might be a raw data folder and s2 might be a processed data folder.
    """
    return s1.difference(s2)


##############################################################
############# Working with YAML config file ##################
##############################################################


def get_yaml_section_keys(
    config_file_path: Union[str, PosixPath],
    section: str
) -> list:
    """
    Returns all the keys within a specific section of YAML config file.
    """
    config_section: dict = read_yaml_config(config_file_path)[section]
    return list(config_section.keys())


def read_yaml_config(
        config_file_path: Union[str, PosixPath]
) -> dict:
    """
    Reads .yaml config file and returns data as a dictionary.
    """
    with open(
        config_file_path,
        'r',
        encoding='utf-8'
    ) as f:
        return yaml.safe_load(f)


def write_yaml_config(
        data: dict,
        config_file_path: Union[str, PosixPath]
) -> None:
    """
    Writes .yaml config file from a dictionary.
    Raises FileExistsError if the supplied path exists to prevent unintentional overwrites.
    """
    if config_file_path.exists():
        raise FileExistsError(
            f"The file {config_file_path} already exists."
        )
    with open(
        config_file_path,
        'w',
        encoding='utf-8'
    ) as f:
        return yaml.dump(data, f)
