from io import StringIO
from pathlib import Path
from typing import Generator, Tuple

import numpy as np
import pandas as pd
import pytest

from ..modules import pressureutils

CONF_SECTION: str = "section1"
LOCS: list[str] = [
    "location1",
    "location2"
]
EXAMPLE_RAW_FILE_PATHS: list[Path] = [
    Path(
        "examples/pressure/location1_raw/160602_PTU300_log.txt"
    ),
    Path(
        "examples/pressure/location2_raw/aws_20160602.lst"
    )
]
EXAMPLE_PROCESSED_FILE_PATHS: list[Path] = [
    Path(
        "examples/pressure/location1_processed/example-location1-20160602.csv"
    ),
    Path(
        "examples/pressure/location2_processed/example-location2-20160602.csv"
    )
]


@pytest.fixture
def mock_config_existing_processed_files(
        tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    content: str = (
        f"{CONF_SECTION}:\n"
        f"  {LOCS[0]}:\n"
        f"    raw_pressure_folder: '{EXAMPLE_RAW_FILE_PATHS[0].parent}'\n"
        f"    raw_file_extension: 'txt'\n"
        f"    parsed_pressure_folder: '{EXAMPLE_PROCESSED_FILE_PATHS[0].parent}'\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
        f"  {LOCS[1]}:\n"
        f"    raw_pressure_folder: {EXAMPLE_RAW_FILE_PATHS[1].parent}\n"
        f"    raw_file_extension: 'lst'\n"
        f"    parsed_pressure_folder: {EXAMPLE_PROCESSED_FILE_PATHS[1].parent}\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
    )
    config: Path = tmp_path_factory.mktemp(
        "tmp_conf"
    )/"tmp_config.yml"
    config.write_text(content)
    return config


@pytest.fixture
def mock_config_no_processed_files(
        tmp_path_factory: pytest.TempPathFactory,
        mock_processed_file_paths: Tuple[Path, Path]
) -> Path:
    content: str = (
        f"{CONF_SECTION}:\n"
        f"  {LOCS[0]}:\n"
        f"    raw_pressure_folder: '{EXAMPLE_RAW_FILE_PATHS[0].parent}'\n"
        f"    raw_file_extension: 'txt'\n"
        f"    parsed_pressure_folder: '{mock_processed_file_paths[0].parent}'\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
        f"  {LOCS[1]}:\n"
        f"    raw_pressure_folder: {EXAMPLE_RAW_FILE_PATHS[1].parent}\n"
        f"    raw_file_extension: 'lst'\n"
        f"    parsed_pressure_folder: {mock_processed_file_paths[1].parent}\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
    )
    config: Path = tmp_path_factory.mktemp(
        "tmp_conf"
    )/"tmp_config.yml"
    config.write_text(content)
    return config


@pytest.fixture(scope="function")
def mock_processed_file_paths(
        tmp_path_factory: pytest.TempPathFactory
) -> Tuple[Path, Path]:
    mock_base_dir = tmp_path_factory.mktemp("mock_pressure")
    loc1_dir = mock_base_dir/"loc1_processed"
    loc2_dir = mock_base_dir/"loc2_processed"
    # Does not create the directories or files so the functions which
    # depend on the files not existing work correctly.
    # Only the correct file path is needed
    return (
        loc1_dir/f"pressure-{LOCS[0]}-20160602.csv",
        loc2_dir/f"pressure-{LOCS[1]}-20160602.csv"
    )


def test_parse_pressure_folder(
        mock_config_no_processed_files: Path,
        # mock_raw_file_paths: Tuple[Path, Path],
        mock_processed_file_paths: Tuple[Path, Path]
) -> None:
    for i, loc in enumerate(LOCS):
        pressureutils.parse_pressure_folder(
            mock_config_no_processed_files,
            CONF_SECTION,
            loc
        )
        assert mock_processed_file_paths[i].exists()


def test_parse_pressure_file(
        tmp_path: Generator[Path, None, None]
) -> None:
    # Verify content of parsed pressure file is correct
    for i, raw_input_path in enumerate(EXAMPLE_RAW_FILE_PATHS):
        mock_output_path: Path = tmp_path/f'tmp_parsed_loc{i}.csv'
        mock_output_path.touch()
        pressureutils.parse_pressure_file(
            raw_input_path,
            mock_output_path
        )
        mock_output_content = mock_output_path.read_text()
        with open(
            EXAMPLE_PROCESSED_FILE_PATHS[i],
            'r',
            encoding='utf-8'
        ) as f:
            example_output_content = f.read()
        assert mock_output_content == example_output_content


def test_apply_pressure_correction() -> None:
    vector = pd.Series([1,2,3,4], dtype=np.float64)
    correction_constant = 0.1
    correction_vector = [1,1,1,1]
    # Constant correction applied
    assert list(pressureutils.apply_pressure_correction(
        vector,
        correction_constant
    )) == [1.1,2.1,3.1,4.1]
    # Vector correction applied
    assert list(pressureutils.apply_pressure_correction(
        vector,
        correction_vector
    )) == [2,3,4,5]
    # No correction applied
    assert list(pressureutils.apply_pressure_correction(
        vector
    )) == list(vector)
    # Test that only accepts a pandas Series
    with pytest.raises(TypeError):
        pressureutils.apply_pressure_correction([1,2,3])
    # Test that vector correction should be correct length
    with pytest.raises(ValueError):
        pressureutils.apply_pressure_correction(
            vector,
            [1,2,3]
        )


def test_generate_unparsed_pressure_file_list(
        mock_config_no_processed_files: Path,
        mock_config_existing_processed_files: Path,
        mock_processed_file_paths: Tuple[Path, Path]
) -> None:
    # Test that when there are no matching processed and raw dates,
    # correct output paths are created for both file types
    for i, loc in enumerate(LOCS):
        unparsed_paths, output_paths = pressureutils.generate_unparsed_pressure_file_list(
            mock_config_no_processed_files,
            CONF_SECTION,
            loc
        )
        assert unparsed_paths == [EXAMPLE_RAW_FILE_PATHS[i]]
        assert output_paths == [mock_processed_file_paths[i]]
    # Test that when there are already processed files for
    # the same dates as raw files, the output is empty
    for loc in LOCS:
        unparsed_paths, output_paths = pressureutils.generate_unparsed_pressure_file_list(
            mock_config_existing_processed_files,
            CONF_SECTION,
            loc
        )
        assert (unparsed_paths, output_paths) == ([], [])


def test_preprocess_case_log_file(
        tmp_path: Generator[Path, None, None]
) -> None:
    content: str = '='
    file: Path = tmp_path/'tmp_raw_file.txt'
    file.write_text(content)
    preprocessed_file: StringIO = pressureutils.preprocess_case_log_file(
        file
    )
    assert preprocessed_file.read() == ' '
