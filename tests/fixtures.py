from pathlib import Path
from typing import Generator, Tuple

import pytest

CONF_SECTION_PRESSURE: str = "pressure"
CONF_SECTION_SYMLINKS: str = "symlinks"
EM27S: list[str] = [
    'SN039', 'SN081', 'SN122'
]
LOCS: list[str] = [
    "location1",
    "location2"
]
EXAMPLE_RAW_FILE_PATHS: Tuple[Tuple[Path], Tuple[Path, Path]] = (
    tuple([
        Path(
        "examples/pressure/location1_raw/160602_PTU300_log.txt"
        )
    ]),
    tuple([
        Path(
            "examples/pressure/location2_raw_collected/aws_20160602.lst"
        ),
        Path(
            "examples/pressure/location2_raw_collected/aws_20170602.lst"
        )
    ])
)
EXAMPLE_PROCESSED_FILE_PATHS: Tuple[Tuple[Path], Tuple[Path, Path]] = (
    tuple([
        Path(
        "examples/pressure/location1_processed/pressure-location1-20160602.csv"
        )
    ]),
    tuple([
        Path(
            "examples/pressure/location2_processed/pressure-location2-20160602.csv"
        ),
        Path(
            "examples/pressure/location2_processed/pressure-location2-20170602.csv"
        )
    ])
)


@pytest.fixture
def mock_config_existing_processed_files(
        tmp_path_factory: pytest.TempPathFactory,
) -> Generator[Path, None, None]:
    """
    This fixture is used for checking how the processing works when there
    are existing processed files.
    """
    content: str = (
        f"{CONF_SECTION_PRESSURE}:\n"
        f"  {LOCS[0]}:\n"
        f"    raw_pressure_folder: '{EXAMPLE_RAW_FILE_PATHS[0][0].parent}'\n"
        f"    raw_file_extension: 'txt'\n"
        f"    parsed_pressure_folder: '{EXAMPLE_PROCESSED_FILE_PATHS[0][0].parent}'\n"
        f"    use_pressure_correction_factor: True\n"
        f"    em27_m: 2\n"
        f"    pressure_sensor_m: '1'\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
        f"  {LOCS[1]}:\n"
        f"    raw_pressure_folder: {EXAMPLE_RAW_FILE_PATHS[1][0].parent}\n"
        f"    raw_file_extension: 'lst'\n"
        f"    parsed_pressure_folder: {EXAMPLE_PROCESSED_FILE_PATHS[1][0].parent}\n"
        f"    use_pressure_correction_factor: True\n"
        f"    em27_m: 2\n"
        f"    pressure_sensor_m: 2\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
    )
    config: Path = tmp_path_factory.mktemp(
        "tmp_conf"
    )/"tmp_config.yml"
    config.write_text(content)
    yield config
    remove_directory_recursively(config.parent)


@pytest.fixture
def mock_config_no_processed_files(
        tmp_path_factory: pytest.TempPathFactory,
        mock_processed_file_paths: Tuple[Tuple[Path], Tuple[Path, Path]]
) -> Generator[Path, None, None]:
    """
    This fixture is used for checking how the processing works when there
    are NO existing processed files.
    """
    content: str = (
        f"{CONF_SECTION_PRESSURE}:\n"
        f"  {LOCS[0]}:\n"
        f"    raw_pressure_folder: '{EXAMPLE_RAW_FILE_PATHS[0][0].parent}'\n"
        f"    raw_file_extension: 'txt'\n"
        f"    parsed_pressure_folder: '{mock_processed_file_paths[0][0].parent}'\n"
        f"    use_pressure_correction_factor: True\n"
        f"    em27_m: 2\n"
        f"    pressure_sensor_m: 1\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
        f"  {LOCS[1]}:\n"
        f"    raw_pressure_folder: {EXAMPLE_RAW_FILE_PATHS[1][0].parent}\n"
        f"    raw_file_extension: 'lst'\n"
        f"    parsed_pressure_folder: {mock_processed_file_paths[1][0].parent}\n"
        f"    use_pressure_correction_factor: True\n"
        f"    em27_m: 2\n"
        f"    pressure_sensor_m: 1\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
    )
    config: Path = tmp_path_factory.mktemp(
        "tmp_conf"
    )/"tmp_config.yml"
    config.write_text(content)
    yield config
    remove_directory_recursively(config.parent)


@pytest.fixture
def mock_config_pressure_correction_cases(
        tmp_path_factory: pytest.TempPathFactory,
) -> Generator[Path, None, None]:
    """
    This fixture is used for checking elevation data cases.
    """
    content: str = (
        f"{CONF_SECTION_PRESSURE}:\n"
        f"  l1:\n"
        f"    raw_pressure_folder: 'NA'\n"
        f"    raw_file_extension: 'txt'\n"
        f"    parsed_pressure_folder: 'NA'\n"
        f"    use_pressure_correction_factor: True\n"
        f"    em27_m: 2\n"
        f"    pressure_sensor_m: '1'\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
        f"  l2:\n"
        f"    raw_pressure_folder: 'NA'\n"
        f"    raw_file_extension: 'lst'\n"
        f"    parsed_pressure_folder: 'NA'\n"
        f"    use_pressure_correction_factor: True\n"
        f"    em27_m:\n"
        f"    pressure_sensor_m: 0.0\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
        f"  l3:\n"
        f"    raw_pressure_folder: 'NA'\n"
        f"    raw_file_extension: 'txt'\n"
        f"    parsed_pressure_folder: 'NA'\n"
        f"    use_pressure_correction_factor: True\n"
        f"    em27_m: 2\n"
        f"    pressure_sensor_m: 'h'\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
        f"  l4:\n"
        f"    raw_pressure_folder: 'NA'\n"
        f"    raw_file_extension: 'lst'\n"
        f"    parsed_pressure_folder: 'NA'\n"
        f"    use_pressure_correction_factor: False\n"
        f"    em27_m: 2\n"
        f"    pressure_sensor_m: '1'\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
        f"  l5:\n"
        f"    raw_pressure_folder: 'NA'\n"
        f"    raw_file_extension: 'lst'\n"
        f"    parsed_pressure_folder: 'NA'\n"
        f"    use_pressure_correction_factor:\n"
        f"    em27_m: 2\n"
        f"    pressure_sensor_m: '1'\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
        f"  l6:\n"
        f"    raw_pressure_folder: 'NA'\n"
        f"    raw_file_extension: 'lst'\n"
        f"    parsed_pressure_folder: 'NA'\n"
        f"    use_pressure_correction_factor: 'yes'\n"
        f"    em27_m: 2\n"
        f"    pressure_sensor_m: '1'\n"
        f"    start_date: '2016-06-02'\n"
        f"    end_date:\n"
    )
    config: Path = tmp_path_factory.mktemp(
        "tmp_conf"
    )/"tmp_config.yml"
    config.write_text(content)
    yield config
    remove_directory_recursively(config.parent)


@pytest.fixture
def mock_config_section_ifg_symlinks(
        tmp_path_factory: pytest.TempPathFactory,
        mock_ifg_target_link_folders: Tuple[Path, list[Path], Path, list[Path]]
) -> Generator[Path, None, None]:
    """
    This fixture is used for testing writing symlinks of EM27 ifg folders,
    which may need to be transformed from 2 digit years to 4 digit years.
    """
    link_folder, _, target_folder, _ = mock_ifg_target_link_folders
    content: str = (
        f"{CONF_SECTION_SYMLINKS}:\n"
        f"  {EM27S[0]}:\n"
        f"    target_folders: \n        - {target_folder}\n"
        f"    link_folder: '{link_folder}'\n"
        f"  {EM27S[1]}:\n"
        f"    target_folders: \n        - {target_folder}\n"
        f"    link_folder: '{link_folder}'\n"
        f"  {EM27S[2]}:\n"
        f"    target_folders: \n        - {target_folder}\n"
        f"    link_folder: '{link_folder}'\n"
    )
    config: Path = tmp_path_factory.mktemp(
        "tmp_conf"
    )/"tmp_config.yml"
    config.write_text(content)
    yield config
    remove_directory_recursively(config.parent)


@pytest.fixture(scope="function")
def mock_processed_file_paths(
        tmp_path_factory: pytest.TempPathFactory
) -> Generator[Tuple[Tuple[Path], Tuple[Path, Path]], None, None]:
    mock_base_dir = tmp_path_factory.mktemp("mock_pressure")
    # Does not create the directories or files so the functions which
    # depend on the files not existing work correctly.
    # Test functions may create these items as needed
    yield (
        tuple([
            mock_base_dir/LOCS[0]/f"pressure-{LOCS[0]}-20160602.csv"
        ]),
        tuple([
            mock_base_dir/LOCS[1]/f"pressure-{LOCS[1]}-20160602.csv",
            mock_base_dir/LOCS[1]/f"pressure-{LOCS[1]}-20170602.csv"
        ])
    )
    remove_directory_recursively(mock_base_dir)


@pytest.fixture(scope="function")
def mock_target_link_folders(
    tmp_path_factory: pytest.TempPathFactory
) -> Generator[Tuple[Path, list[Path], Path, list[Path]], None, None]:
    link_folder: Path = tmp_path_factory.mktemp("link_folder")
    link_paths: list[Path] = [
        link_folder/'test0_dir',
        link_folder/'test1.file',
        link_folder/'test2.file'
    ]
    target_folder: Path = tmp_path_factory.mktemp("target_folder")
    target_paths: list[Path] = [
        target_folder/'test0_dir',
        target_folder/'test1.file',
        target_folder/'test2.file'
    ]
    # only create target_paths in the file system, do not create link_paths
    for i, path in enumerate(target_paths):
        if i == 0:
            path.mkdir()
        else:
            path.touch()
    yield link_folder, link_paths, target_folder, target_paths
    remove_directory_recursively(link_folder)
    remove_directory_recursively(target_folder)


@pytest.fixture(scope="function")
def mock_ifg_target_link_folders(
    tmp_path_factory: pytest.TempPathFactory
) -> Generator[Tuple[Path, list[Path], Path, list[Path]], None, None]:
    link_folder: Path = tmp_path_factory.mktemp("link_folder")
    link_paths: list[Path] = [
        link_folder/'19960229',
        link_folder/'20001231',
        link_folder/'20200814',
        link_folder/'20500606'
    ]
    target_folder: Path = tmp_path_factory.mktemp("target_folder")
    target_paths: list[Path] = [
        target_folder/'19960229',
        target_folder/'001231',
        target_folder/'20200814',
        target_folder/'500606'
    ]
    # only create target_paths in the file system, do not create link_paths
    for i, path in enumerate(target_paths):
        if i == 0:
            path.mkdir()
        else:
            path.touch()
    yield link_folder, link_paths, target_folder, target_paths
    remove_directory_recursively(link_folder)
    remove_directory_recursively(target_folder)


def remove_directory_recursively(input_path: Path):
    for child in input_path.iterdir():
        if child.is_file() or child.is_symlink():
            child.unlink()
        else:
            remove_directory_recursively(child)
    input_path.rmdir()
