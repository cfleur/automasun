import datetime as dt

from pathlib import Path

import pandas as pd
import pytest


from ..modules import ioutils


DATES = [
    dt.datetime(2016, 6, 2).date(),
    dt.datetime(2016, 6, 3).date(),
    dt.datetime(2016, 6, 4).date()
]
LOC = "loc"
FILENAMES = [
    "aws_20160602.lst",
    "160603_PTU300_log.txt",
    f"pressure-{LOC}-20160604.csv",
    "fail_file_004762"
]
FILETYPES = ['lst', 'txt', 'csv', 'fail_extension']

MOCK_CSV_DIRNAME: str = "tmp_csv"
MOCK_CSV_FILENAME: str = "tmp_csv_file.csv"

LOCATIONS = (
    "location1",
    "location2"
)


@pytest.fixture()
def mock_files(
        tmp_path_factory
) -> list[Path]:
    files = []
    mock_dir = tmp_path_factory.mktemp("tmp_files")
    for f in FILENAMES[0:3]:
        file: Path = mock_dir/f
        file.touch()
        files.append(file)
    return files


@pytest.fixture()
def mock_csv(
        tmp_path_factory: pytest.TempPathFactory
) -> Path:
    content: str = (
        "column1,column2,column3\n"
        "value11,value12,value13\n"
        "value21,value22,value23\n"
    )
    file: Path = tmp_path_factory.mktemp(
        MOCK_CSV_DIRNAME, numbered=True
    )/MOCK_CSV_FILENAME
    file.write_text(content)
    return file


@pytest.fixture
def mock_config_dict():
    return {
        LOCATIONS[0]: {
            "key11": None,
            "key12": None
        },
        LOCATIONS[1]: {
            "key21": None
        }
    }


@pytest.fixture
def mock_config(
    tmp_path_factory: pytest.TempPathFactory
) -> Path:
    content: str = (
        f"{LOCATIONS[0]}:\n"
        f"  key11:\n"
        f"  key12:\n"
        f"{LOCATIONS[1]}:\n"
        f"  key21:\n"
    )
    config: Path = tmp_path_factory.mktemp(
        "tmp_conf"
    )/"tmp_config.yml"
    config.write_text(content)
    return config


############## Working with file name dates ##################

def test_generate_file_list_from_dates() -> None:
    # Test that correct file names are returned
    filelist = []
    for i, ft in enumerate(FILETYPES):
        try:
            fl = ioutils.generate_file_list_from_dates(
                DATES, ft, LOC
            )
            filelist.append(fl[i])
        except ValueError:
            # 'fail_extension' should throw a value error
            ...
    assert filelist == FILENAMES[0:3]
    # Test that TypeError is thrown when input is not a list or set
    g = None
    try:
        g = ioutils.generate_file_list_from_dates(
            "failure_input", " "
        )
    except TypeError:
        ...
    assert g is None


def test_generate_fname_from_date() -> None:
    filenames = []
    dates = DATES.copy()
    dates.append(0)
    # Test correct filenames are generated
    for (d, ft) in zip(dates, FILETYPES):
        try:
            f = ioutils.generate_fname_from_date(
                d, ft, LOC
            )
            filenames.append(f)
        except ValueError:
            ...
    assert filenames == FILENAMES[0:3]
    # Test exception on missing location
    g = None
    try:
        g = ioutils.generate_fname_from_date(
            dt.datetime.now(),
            'csv',
            location=None
        )
    except ValueError:
        # missing location throws a value error for 'cs' type
        ...
    assert g is None


def test_generate_date_list_from_folder(
        mock_files: list[Path]
) -> None:
    mock_dir = mock_files[0].parent
    dates = ioutils.generate_date_list_from_folder(
        mock_dir,
        start_date = DATES[0],
        end_date = DATES[-1]
    )
    assert dates == sorted(DATES)


def test_extract_date_from_fname() -> None:
    dates = []
    for f in FILENAMES:
        try:
            d = ioutils.extract_date_from_fname(f)
            dates.append(d)
        except ValueError:
            ...
    assert dates == DATES


def test_generate_set_difference() -> None:
    raw_folder: set = {'file1','file2','file3'}
    processed_folder: set = {'file1', 'file2'}
    unprocessed_files: set = ioutils.generate_set_difference(
        raw_folder,
        processed_folder
    )
    assert {'file3'} == unprocessed_files


################### Working with files #######################

# TODO:
# def test_separate_mod_vmr_map


# TODO:
# def_test_filter_move_files


def test_create_file_path() -> None:
    path = ioutils.create_file_path(
        MOCK_CSV_DIRNAME,
        MOCK_CSV_FILENAME,
        create_dir = True
    )
    assert path.parent.is_dir()
    path.parent.rmdir()
    assert path == Path(MOCK_CSV_DIRNAME)/MOCK_CSV_FILENAME


def test_get_file_extension(
        mock_csv: Path
) -> None:
    assert ioutils.get_file_extension(mock_csv) == 'csv'


def test_read_file_names(
        mock_csv: Path
) -> None:
    path = mock_csv.parent
    filename = ioutils.read_file_names(path)[0]
    assert filename == MOCK_CSV_FILENAME


############# Working with YAML config file ##################

def test_get_yaml_section_keys(
        mock_config: Path,
) -> None:
    keys = ioutils.get_yaml_section_keys(
        mock_config, LOCATIONS[0]
    )
    assert keys == ["key11", "key12"]


def test_read_yaml_config(
        mock_config: Path,
        mock_config_dict: dict
) -> None:
    assert ioutils.read_yaml_config(mock_config) == mock_config_dict


############## CSV and HDF file operations ###################

def test_get_csv_col(
        mock_csv: Path
) -> None:
    col_number: int = 1
    df: pd.DataFrame = pd.read_csv(mock_csv)
    mock_col: pd.Series = df[df.columns[col_number]]
    csv_col: pd.Series = ioutils.get_csv_col(mock_csv, col_number)
    assert list(csv_col) == list(mock_col)


def test_get_csv_keys(
        mock_csv: Path
) -> None:
    mock_keys: pd.Index = pd.read_csv(mock_csv).keys()
    csv_keys: pd.Index = ioutils.get_csv_keys(mock_csv)
    assert list(csv_keys) == list(mock_keys)


# TODO:
# def test_get_hdf_col


# TODO:
# def test_get_hdf_keys
