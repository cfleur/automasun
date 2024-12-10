import os

from pathlib import Path
from typing import Generator, Tuple

import pytest

from ..modules import pipeline, ioutils
from .fixtures import (
    mock_config_existing_processed_files,
    mock_config_no_processed_files,
    mock_processed_file_paths,
    LOCS,
    EXAMPLE_PROCESSED_FILE_PATHS
)


# @pytest.mark.only
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


# @pytest.mark.only
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


# @pytest.mark.only
def test_prepare_pressure_config_file(
        tmp_path: Generator[Path, None, None]
):
    """
    Test cases based in example config file found in examples/.
    """
    example_config_file: Path = Path(
        "examples/example_pipeline_config.yml"
    )
    assert example_config_file.exists()
    assert example_config_file.is_file()
    # Test that existing processed files are not modified
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
    # Test that correct output is given based on example config file
    # i.e. that the pressure is correctly parsed and the correction
    # factor (calibration) is correctly applied based on elevations
    config: dict = ioutils.read_yaml_config(
        example_config_file
    )
    # change output paths to temp locations so that
    # pressure parsing is not skipped
    mock_output_paths: list[Path] = []
    example_output_paths: list[Path] = []
    for i, loc in enumerate(config['pressure']):
        example_output_path = config['pressure'][loc]['parsed_pressure_folder']
        example_output_paths.append(
            Path(example_output_path)
        )
        mock_output_dir: Path = tmp_path/loc
        config['pressure'][loc]['parsed_pressure_folder'] = str(mock_output_dir)
        mock_output_paths.append(
            mock_output_dir/f'{EXAMPLE_PROCESSED_FILE_PATHS[i].name}'
        )
    # write a new temp config file with temp paths
    # as pipeline requires a file path as an argument
    mock_config_path: Path = tmp_path/'mock_config_file.yml'
    ioutils.write_yaml_config(
        data=config,
        config_file_path=mock_config_path
    )
    assert mock_config_path.is_file()
    del config # clean up config object, its no longer needed
    pipeline.prepare_pressure(
        mock_config_path
    )
    for mock_output_path, example_output_path in zip(
        mock_output_paths, EXAMPLE_PROCESSED_FILE_PATHS
    ):
        assert mock_output_path.exists()
        assert mock_output_path.read_text() == example_output_path.read_text()
