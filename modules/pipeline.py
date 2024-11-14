import os
import sys
from pathlib import Path

from . import pressureutils, ioutils

# environment with MAIN_CONFIG_DIR pointing to configuration files required
# for example, export a .env file:
# export $(grep -v '^#' <path-to-env> | xargs)
CONFIG_FOLDER: Path = Path(os.getenv('MAIN_CONFIG_DIR'))
CONFIG_FILE: Path = CONFIG_FOLDER/"FMIpipelineutils/fmi_pipeline_config.yml"


def prepare_pressure(
        config_file: Path
) -> None:
    # TODO: add test
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
