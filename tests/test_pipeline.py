import os

from pathlib import Path
from typing import Generator, Tuple

import pytest

from ..modules import pipeline, ioutils
from .fixtures import (
    mock_config_existing_processed_files,
    mock_config_no_processed_files,
    mock_config_section_ifg_symlinks,
    mock_ifg_target_link_folders,
    mock_processed_file_paths,
    remove_directory_recursively,
    LOCS,
    EXAMPLE_PROCESSED_FILE_PATHS,
    CONF_SECTION_SYMLINKS
)


@pytest.mark.integration
def test_setup_environment() -> None:
    pipeline.setup_environment()


# @pytest.mark.only
def test_prepare_pressure_existing(
        mock_config_existing_processed_files: Path
) -> None:
    # Test pipeline does not modify folder contents when processed files exist
    time_0: list[float] = []
    for loc_paths in EXAMPLE_PROCESSED_FILE_PATHS:
        for file_path in loc_paths:
            time_0.append(
                os.path.getmtime(
                    file_path
                )
            )
    pipeline.prepare_pressure(
        mock_config_existing_processed_files
    )
    time_1: list[float] = []
    for loc_paths in EXAMPLE_PROCESSED_FILE_PATHS:
        for file_path in loc_paths:
            time_1.append(
                os.path.getmtime(file_path)
            )
    assert time_0 == time_1
    # TODO: reduce test redundancy by using example config
    # mock_config_existing _processed_files may be replaced
    # by real example config. test_prepare_pressure_config_file
    # does the same as this test with real example config file.


# @pytest.mark.only
def test_prepare_pressure_no_existing(
        mock_config_no_processed_files: Path,
        mock_processed_file_paths: Tuple[Tuple[Path], Tuple[Path, Path]]
) -> None:
    # Test that pipeline creates correct folders and files from config
    pipeline.prepare_pressure(
        mock_config_no_processed_files
    )
    for i, loc in enumerate(LOCS):
        for file_path in mock_processed_file_paths[i]:
            parsed_pressure_folder: Path = file_path.parent
            parsed_pressure_file: Path = file_path
            assert parsed_pressure_folder.exists()
            assert parsed_pressure_folder.name == loc
            assert parsed_pressure_file.exists()


# @pytest.mark.only
def test_prepare_pressure_config_file(
        tmp_path: Generator[Path, None, None]
) -> None:
    """
    Test cases based in example config file found in examples/.
    """
    example_config_file: Path = Path(
        "examples/example_pipeline_config.yml"
    )
    assert example_config_file.exists()
    assert example_config_file.is_file()
    # Test that existing processed files are not modified
    # based on paths in example config file
    time_0: list[float] = []
    for loc_paths in EXAMPLE_PROCESSED_FILE_PATHS:
        for file_path in loc_paths:
            time_0.append(
                os.path.getmtime(
                    file_path
                )
            )
    pipeline.prepare_pressure(
        example_config_file
    )
    time_1: list[float] = []
    for loc_paths in EXAMPLE_PROCESSED_FILE_PATHS:
        for file_path in loc_paths:
            time_1.append(
                os.path.getmtime(file_path)
            )
    assert time_0 == time_1

    # Test that correct output is given based on example config file
    # i.e. that the pressure is correctly parsed and the correction
    # factor (calibration) is correctly applied based on elevations.
    # Config file output paths are modified to temp locations for these tests.
    config: dict = ioutils.read_yaml_config(
        example_config_file
    )
    # change output paths to temp locations so that
    # pressure parsing is not skipped
    mock_output_paths: list[list[Path]] = []
    for i, loc in enumerate(config['pressure']):
        mock_output_dir: Path = tmp_path/loc
        config['pressure'][loc]['parsed_pressure_folder'] = str(mock_output_dir)
        # create list of mock output paths for comparison to example files
        mock_output_paths.append([])
        for processed_path in EXAMPLE_PROCESSED_FILE_PATHS[i]:
            mock_output_paths[i].append(
                mock_output_dir/f'{processed_path.name}'
            )
    # write a new temp config file with temp paths
    # as pipeline requires a file path as an argument
    mock_config_path: Path = tmp_path/'mock_config_file.yml'
    ioutils.write_yaml_config(
        data=config,
        config_file_path=mock_config_path
    )
    assert mock_config_path.is_file()
    del config # clean up config object, no longer needed
    pipeline.prepare_pressure(
        mock_config_path
    )
    for mock_loc_paths, loc_paths in zip(mock_output_paths, EXAMPLE_PROCESSED_FILE_PATHS):
        for mock_output_path, example_output_path in zip(
            mock_loc_paths, loc_paths
        ):
            assert mock_output_path.exists()
            assert mock_output_path.read_text() == example_output_path.read_text()
    # clean up
    remove_directory_recursively(tmp_path)


# @pytest.mark.only
def test_prepare_symlinks(
        tmp_path: Generator[Path, None, None]
) -> None:
    """
    Test cases based in example config file found in examples/.
    """
    example_config_file: Path = Path(
        "examples/example_pipeline_config.yml"
    )
    assert example_config_file.exists()
    assert example_config_file.is_file()
    config: dict = ioutils.read_yaml_config(
        example_config_file
    )
    # Test that existing processed files are not modified
    # based on paths in example config file
    symlink_jobs: list = ioutils.get_yaml_section_keys(
        example_config_file,
        CONF_SECTION_SYMLINKS
    )
    target_paths: list[Path] = []
    for job in symlink_jobs:
        for target_folder in config[CONF_SECTION_SYMLINKS][job]['target_folders']:
            for file_path in Path(target_folder).glob('*'):
                target_paths.append(
                    file_path
                )
    time_0: list[float] = []
    for target_path in sorted(
         target_paths,
         key=lambda p: p.name
    ):
        time_0.append(
            os.path.getmtime(
                target_path
            )
        )
    pipeline.prepare_pressure(
        example_config_file
    )
    time_1: list[float] = []
    for job in symlink_jobs:
        for link_path in sorted(
            Path(config[CONF_SECTION_SYMLINKS][job]['link_folder']).resolve().glob('*'),
            key=lambda p: p.name
        ):
            time_1.append(
                os.path.getmtime(
                    link_path
                )
            )
    assert time_0 == time_1

    # Test that correct output is given based on example config file
    # i.e. that correct symlinks are created.
    mock_folders: list[str] = []
    for job in symlink_jobs:
        # create temp output directories to write symlinks to
        mock_link_folder: Path = tmp_path/f'mock_link_folder_{job}'
        mock_folders.append(
            mock_link_folder
        )
        config[CONF_SECTION_SYMLINKS][job]['link_folder'] = str(mock_link_folder)
    # write a new temp config file with temp paths
    mock_config_path: Path = tmp_path/'mock_config_file.yml'
    ioutils.write_yaml_config(
        data=config,
        config_file_path=mock_config_path
    )
    assert mock_config_path.is_file()
    pipeline.prepare_symlinks(
        mock_config_path
    )
    for job in symlink_jobs:
        target_paths: list[Path] = []
        for target_folder in config[CONF_SECTION_SYMLINKS][job]['target_folders']:
            for target_path in list(Path(target_folder).glob('*')):
                target_paths.append(
                   target_path
                )
        link_paths: list[Path] = Path(
                config[CONF_SECTION_SYMLINKS][job]['link_folder']
            ).glob('*')
        assert sorted(
            list(t.resolve() for t in target_paths),
            key=lambda p: p.name
        ) == sorted(
            list(t.readlink() for t in link_paths),
            key=lambda p: p.name
        )
    # clean up
    remove_directory_recursively(tmp_path)


# @pytest.mark.only
def test_prepare_symlinks_ifg(
        mock_config_section_ifg_symlinks: Path,
        mock_ifg_target_link_folders: Tuple[Path, list[Path], Path, list[Path]]
) -> None:
    """
    Test prepare_symlinks when symlinks section of config contains EM27 instruments.
    In this case, folder name dates should be changed from 2 digit years to 4 digit years
    if they are not already 4 digit years.
    """
    assert mock_config_section_ifg_symlinks.exists()
    assert mock_config_section_ifg_symlinks.is_file()

    # Test that correct output is given based on mock config file
    # i.e. that correct symlinks are created.
    pipeline.prepare_symlinks(
        mock_config_section_ifg_symlinks
    )
    link_folder, link_paths, _, _ = mock_ifg_target_link_folders
    created_links = sorted(
        link_folder.glob('*'),
        key=lambda d: d.name
    )
    assert created_links == link_paths
