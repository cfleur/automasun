import datetime as dt

from contextlib import nullcontext
from pathlib import Path
from typing import Generator

import pytest
import yaml

from modules import ioutils


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
        tmp_path_factory: pytest.TempPathFactory
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

# @pytest.mark.only
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


# @pytest.mark.only
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


# @pytest.mark.only
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


# @pytest.mark.only
def test_extract_date_from_fname() -> None:
    dates = []
    for f in FILENAMES:
        try:
            d = ioutils.extract_date_from_fname(f)
            dates.append(d)
        except ValueError:
            ...
    assert dates == DATES


# @pytest.mark.only
@pytest.mark.parametrize(
    "date, expectation",
    [
        pytest.param(
            dt.datetime(2000, 12, 31), nullcontext('20001231'), id='datetime_object'
        ),
        pytest.param(
            'different object', pytest.raises(TypeError), id='not_datetime_object'
        )
    ]
)
def test_generate_dirname_from_date(
        date, expectation
) -> None:
    with expectation as e:
        assert ioutils.generate_dirname_from_date(
            date
        ) == e


# @pytest.mark.only
@pytest.mark.parametrize(
    "dirname, expectation",
    [
        pytest.param(
            '20001231', nullcontext(dt.datetime(2000, 12, 31)), id='dirname_format_Ymd'
        ),
        pytest.param(
            '001231', nullcontext(dt.datetime(2000, 12, 31)), id='dirname_format_ymd'
        ),
        pytest.param(
            'different dirname format', pytest.raises(ValueError), id='wrong_dirname_format'
        )
    ]
)
def test_extract_date_from_dirname(
        dirname, expectation
) -> None:
    with expectation as e:
        assert ioutils.extract_date_from_dirname(
            dirname
        ) == e


# @pytest.mark.only
def test_generate_set_difference() -> None:
    raw_folder: set = {'file1','file2','file3'}
    processed_folder: set = {'file1', 'file2'}
    empty_folder: set = set()
    unprocessed_files: set = ioutils.generate_set_difference(
        raw_folder,
        processed_folder
    )
    assert {'file3'} == unprocessed_files
    # Test with empty folder
    unprocessed_files: set = ioutils.generate_set_difference(
        empty_folder,
        processed_folder
    )
    assert set() == unprocessed_files
    unprocessed_files: set = ioutils.generate_set_difference(
        raw_folder,
        empty_folder
    )
    assert raw_folder == unprocessed_files


################### Working with files #######################

# TODO:
# def test_separate_mod_vmr_map


# TODO:
# def_test_filter_move_files


# @pytest.mark.only
def test_get_file_extension(
        mock_csv: Path
) -> None:
    assert ioutils.get_file_extension(mock_csv) == 'csv'


# @pytest.mark.only
def test_read_file_names(
        mock_csv: Path
) -> None:
    path = mock_csv.parent
    filename = ioutils.read_file_names(path)[0]
    assert filename == MOCK_CSV_FILENAME


############# Working with YAML config file ##################

# @pytest.mark.only
def test_get_yaml_section_keys(
        mock_config: Path,
) -> None:
    keys = ioutils.get_yaml_section_keys(
        mock_config, LOCATIONS[0]
    )
    assert keys == ["key11", "key12"]


# @pytest.mark.only
def test_read_yaml_config(
        mock_config: Path,
        mock_config_dict: dict
) -> None:
    assert ioutils.read_yaml_config(
        mock_config
    ) == mock_config_dict


# @pytest.mark.only
def test_write_yaml_config(
        mock_config_dict: dict,
        tmp_path: Generator[Path, None, None]
) -> None:
    # Test that data written is correct.
    mock_config_path: Path = tmp_path/'mock_config.yml'
    input_data = mock_config_dict
    ioutils.write_yaml_config(
        data=input_data,
        config_file_path=mock_config_path
    )
    with open(
        mock_config_path,
        'r',
        encoding='utf-8'
    ) as f:
        loaded_data = yaml.safe_load(f)
    assert loaded_data == input_data
    # Test that existing file is not overwritten
    with pytest.raises(
        FileExistsError
    ):
        ioutils.write_yaml_config(
            data=input_data,
            config_file_path=mock_config_path
        )
