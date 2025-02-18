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
from typing import Union

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


def prepare_pressure(
        config_file: Union[Path, None] = None
) -> None:
    """
    Reads config file and collects locations to process and
    passes them to a function that parses pressure folders
    for those locations.
    """
    if config_file is None:
        config_file = setup_environment()
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
        config_file: Union[Path, None] = None
) -> None:
    """
    Reads config file and collects symlinks into a link folder for all files in target folders.
    When processing EM27 instrument interferogram folders, the folder name is checked to be in
    format yyyymmdd. If it is not (i.e. in format yymmdd with only 2 digit years), the symlink
    name will be changed to yyyymmdd (4 digit year).
    """
    if config_file is None:
        config_file = setup_environment()
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
    EM27_instruments: list[str] = [
        'SN039', 'SN081', 'SN122'
    ]
    link_names: Union[tuple[str], None] = None
    for job_name in symlink_jobs:
        # NOTE: if there are differences between pressure and interferogram symlinks processing
        # they can be handled them here e.g. by conditioning on the job name
        target_folders: list[str] = config[symlink_config_section][job_name]["target_folders"]
        link_folder: str = config[symlink_config_section][job_name]["link_folder"]
        for target_folder in target_folders:
            link_names: Union[tuple[str], None] = None
            try:
                if job_name in EM27_instruments:
                    print(
                        f"\n > Creating symlinks for {job_name} interferograms."
                    )
                    target_items = sorted(
                        Path(target_folder).glob('*'),
                        key=lambda p: p.name
                    ) # same sorting key as in write_symlinks
                    link_names = tuple(
                        ioutils.generate_dirname_from_date(
                            ioutils.extract_date_from_dirname(
                                item.name
                            )
                        )
                        for item in target_items
                    )
                _ = syncutils.write_symlinks(
                    target_folder, link_folder, link_names=link_names,
                    resolve_path=resolve_path, v=v
                )
            except ValueError as e:
                print(
                    f"! Error, skipping '{target_folder}'. Could not parse folder date. Perhaps there are non-ifg folders in this directory?"
                    " Please supply a directory which only has interferogram measurement folders.\n", e
                )


if __name__ == "__main__":
    args: list = sys.argv
    start_time_utc: dt.datetime = dt.datetime.now(dt.timezone.utc)
    print(f'\n-- LOG {start_time_utc} {args[0]} {args[1]} started --')
    if len(args) > 1:
        globals()[args[1]](*args[2:])
    end_time_utc: dt.datetime = dt.datetime.now(dt.timezone.utc)
    run_time_delta: dt.timedelta = end_time_utc - start_time_utc
    print(f'\n-- LOG {end_time_utc} {args[0]} {args[1]} completed in {run_time_delta} --')
