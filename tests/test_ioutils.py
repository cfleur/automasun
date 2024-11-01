from pathlib import Path

import pandas as pd
import pytest

from ..modules import ioutils


def test_generate_set_difference():
    raw_folder: set = {'file1','file2','file3'}
    processed_folder: set = {'file1', 'file2'}
    unprocessed_files: set = ioutils.generate_set_difference(
        raw_folder,
        processed_folder
    )
    assert {'file3'} == unprocessed_files


@pytest.fixture()
def mock_csv(tmp_path_factory):
    content: str = (
        'column1,column2,column3\n'
        'value11,value12,value13\n'
        'value21,value22,value23\n'
    )
    file: Path = tmp_path_factory.mktemp("tmp")/'tmp_csv_file.txt'
    file.write_text(content)
    return file


def test_get_csv_col(mock_csv):
    col_number: int = 1
    df: pd.DataFrame = pd.read_csv(mock_csv)
    mock_col: pd.Series = df[df.columns[col_number]]
    csv_col: pd.Series = ioutils.get_csv_col(mock_csv, col_number)
    assert list(mock_col) == list(csv_col)


def test_get_csv_keys(mock_csv):
    mock_keys: pd.Index = pd.read_csv(mock_csv).keys()
    csv_keys: pd.Index = ioutils.get_csv_keys(mock_csv)
    assert list(mock_keys) == list(csv_keys)
