import sys
from pathlib import Path

from dotenv import Dotenv

from . import pressureutils


def prepare_pressure() -> None:
    env = Dotenv(".env")
    config_folder = Path(env.get('MAIN_CONFIG_DIR'))
    prepare_pressure_config_file = config_folder/"FMIpipelineutils/prepare_pressure.yml"
    # TODO: get config keys and loop through all instruments and locations
    instrument = 'SN122'
    location = 'wetland'
    pressureutils.parse_pressure_folder(instrument, location, prepare_pressure_config_file)


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        globals()[args[1]](*args[2:])
    # args[0] = current file
    # args[1] = function name
    # args[2:] = function args : (*unpacked)
