import sys
from pathlib import Path

from dotenv import Dotenv

from . import pressureutils, ioutils


ENV = Dotenv(".env")
CONFIG_FOLDER = Path(ENV.get('MAIN_CONFIG_DIR'))
CONFIG_FILE = CONFIG_FOLDER/"FMIpipelineutils/fmi_pipeline_config.yml"


def prepare_pressure() -> None:
    pressure_config_section = "pressure"
    locations = ioutils.get_yaml_section_keys(
        CONFIG_FILE,
        pressure_config_section
    )
    for location in locations:
        pressureutils.parse_pressure_folder(
            CONFIG_FILE,
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
