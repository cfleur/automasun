"""
The functions in this file can be executed directly in the command line.
The name of the function is the first argument that follows calling the module.
Arguments that that follow are function arguments.
E.g. from root folder:
`python -m modules.FMIpipelineutils.pipeline prepare_pressure alternate_config_file`
When the file is executed as __main__ and not imported (as in above line),
the call to `sys.argv` returns the following:
args[0] = current file
args[1] = function name
args[2:] = function args : (*unpacked)
"""

import datetime as dt
import os
import sys
from pathlib import Path

import dotenv

from . import pressureutils, ioutils, syncutils


def setup_environment() -> Path:
    """
    Environment key `PIPELINE_CONFIG_FILE` pointing to
    configuration file is required. For example,
    - export the variable:
        export PIPELINE_CONFIG_FILE=<path-to-config-file>
    - place a .env file with this variable in project root
    - export a .env file from an alternate location:
        export $(grep -v '^#' <path-to-env> | xargs)
    """
    if os.path.isfile('.env'):
        dotenv.load_dotenv('.env')
    config_file_key = 'PIPELINE_CONFIG_FILE'
    try:
        config_file_path = Path(
            os.getenv(
                config_file_key
            )
        )
    except TypeError:
        print(
            f">>> Could not find {config_file_key} from environment.",
            setup_environment.__doc__
        )
        raise
    if not config_file_path.is_file() or config_file_path.suffix != '.yml':
        raise FileNotFoundError(
            f" Check environment variable {config_file_key}."
            f" '{config_file_path}' is not a .yml file."
        )
    # TODO: check that config file is valid YAML
    return config_file_path


CONFIG_FILE_PATH: Path = setup_environment()


def prepare_pressure(
        config_file: Path = CONFIG_FILE_PATH
) -> None:
    """
    Reads config file and collects locations to process and
    passes them to a function that parses pressure folders
    for those locations.
    """
    v: bool = False # verbose logs
    vv: bool = False # more verbose logs
    pressure_config_section: str = "pressure"
    locations: list = ioutils.get_yaml_section_keys(
        config_file,
        pressure_config_section
    )
    for location in locations:
        pressureutils.parse_pressure_folder(
            config_file,
            pressure_config_section,
            location, v=v, vv=vv
        )


def prepare_symlinks(
        config_file: Path = CONFIG_FILE_PATH
) -> None:
    """
    Reads config file and collects symlinks into a link folder
    for all files in target folders.
    """
    resolve_path: bool = True
    v: bool = False # verbose logs
    config: dict = ioutils.read_yaml_config(
        config_file
    )
    symlink_config_section: str = "symlinks"
    symlink_jobs: list = ioutils.get_yaml_section_keys(
        config_file,
        symlink_config_section
    )
    for job in symlink_jobs:
        # NOTE: if there are differences between pressure and interferrogram symlinks processing
        # they can be handled them here e.g. by conditioning on the job name
        target_folders: list[str] = config[symlink_config_section][job]["target_folders"]
        link_folder: str = config[symlink_config_section][job]["link_folder"]
        for target_folder in target_folders:
            _ = syncutils.write_symlinks(
                target_folder, link_folder,
                resolve_path=resolve_path, v=v
            )


if __name__ == "__main__":
    args = sys.argv
    print(args[0], dt.datetime.now(dt.timezone.utc), 'log:')
    if len(args) > 1:
        globals()[args[1]](*args[2:])
