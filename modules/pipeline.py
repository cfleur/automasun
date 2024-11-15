import os
import sys
from pathlib import Path

from . import pressureutils, ioutils

def setup_environment() -> Path:
    """
    Environment key `PIPELINE_CONFIG_FILE` pointing to
    configuration file is required,for example, export a .env file:
    export $(grep -v '^#' <path-to-env> | xargs)
    """
    config_file_key = 'PIPELINE_CONFIG_FILE'
    return Path(os.getenv(config_file_key))


CONFIG_FILE: Path = setup_environment()
# TODO: create integration test cases to check user config exists/is valid


def prepare_pressure(
        config_file: Path = CONFIG_FILE
) -> None:
    """
    Reads config file and collects locations to process and
    passes them to a function that parses pressure folders
    for those locations.
    """
    pressure_config_section = "pressure"
    locations = ioutils.get_yaml_section_keys(
        config_file,
        pressure_config_section
    )
    for location in locations:
        pressureutils.parse_pressure_folder(
            config_file,
            pressure_config_section,
            location
        )


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        globals()[args[1]](*args[2:])
    # args[0] = current file
    # args[1] = function name
    # args[2:] = function args : (*unpacked)
