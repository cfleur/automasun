import os

from pathlib import Path
from typing import Tuple

from ..modules import pipeline
from .fixtures import (
    mock_config_existing_processed_files,
    mock_config_no_processed_files,
    mock_processed_file_paths,
    LOCS,
    EXAMPLE_PROCESSED_FILE_PATHS
)

# TODO: check that pipeline.prepare_pressure actually finds the files
# and parses them, e.g. by tracking number of files found and parsed
# in respective functions
# currently, making tests fail (e.g. assert 0) shows print out from
# from parse_pressure_folder - pandas writing to csv sees mock paths
# as directories and this function doesn't actually write the files


def test_prepare_pressure_existing(
        mock_config_existing_processed_files: Path
):
    # Test pipeline does not modify folder contents when processed files exist
    time_0: list[float] = []
    for file_path in EXAMPLE_PROCESSED_FILE_PATHS:
        time_0.append(
            os.path.getmtime(
                file_path
            )
        )
    pipeline.prepare_pressure(
        mock_config_existing_processed_files
    )
    write_time_comparisons: list[bool] = []
    for file_path, t0 in zip(EXAMPLE_PROCESSED_FILE_PATHS, time_0):
        write_time_comparisons.append(
            os.path.getmtime(file_path) == t0
        )
    assert False not in write_time_comparisons


def test_prepare_pressure_no_existing(
        mock_config_no_processed_files: Path,
        mock_processed_file_paths: Tuple[Path, Path],
):
    # Test that pipeline creates correct folders and files from config
    pipeline.prepare_pressure(
        mock_config_no_processed_files
    )
    for i, loc in enumerate(LOCS):
        parsed_pressure_folder: Path = mock_processed_file_paths[i].parent
        parsed_pressure_file: Path = mock_processed_file_paths[i]
        assert parsed_pressure_folder.exists()
        assert parsed_pressure_folder.name == loc
        assert parsed_pressure_file.exists()


def test_prepare_pressure_config_file():
    example_config_file: Path = Path(
        "examples/example_pipeline_config.yml"
    )
    assert example_config_file.exists()
    assert example_config_file.is_file()
    time_0: list[float] = []
    for file_path in EXAMPLE_PROCESSED_FILE_PATHS:
        time_0.append(
            os.path.getmtime(
                file_path
            )
        )
    pipeline.prepare_pressure(
        example_config_file
    )
    write_time_comparisons: list[bool] = []
    for file_path, t0 in zip(EXAMPLE_PROCESSED_FILE_PATHS, time_0):
        write_time_comparisons.append(
            os.path.getmtime(file_path) == t0
        )
    assert False not in write_time_comparisons
