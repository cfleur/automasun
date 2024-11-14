from pathlib import Path
from typing import Tuple

import pytest

CONF_SECTION_PRESSURE: str = "pressure"
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
        f"{CONF_SECTION_PRESSURE}:\n"
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
        f"{CONF_SECTION_PRESSURE}:\n"
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
    # Does not create the directories or files so the functions which
    # depend on the files not existing work correctly.
    # Only the correct file path is needed
    return (
        mock_base_dir/LOCS[0]/f"pressure-{LOCS[0]}-20160602.csv",
        mock_base_dir/LOCS[1]/f"pressure-{LOCS[1]}-20160602.csv"
    )
