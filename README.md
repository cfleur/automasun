# Automasun: tools for facilitating ground-based FTIR spectrometry retrieval data

This is a collection of tools for transforming input data to run retrievals with ground-based spectrometry data (e.g. measured with an EM27/SUN instrument), i.e. with [em27-retrieval-pipeline](https://github.com/tum-esm/em27-retrieval-pipeline) or [PROFFASTpylot](https://gitlab.eudat.eu/coccon-kit/proffastpylot).

The main tools are configured in a YAML file and do the following:
- create symlinks for working with different folder structures to either use the parse pressure tools in this repository or use the retrieval batch precessing pipeline at [em27-retrieval-pipeline](https://github.com/tum-esm/em27-retrieval-pipeline) (see `examples/pressure/location2_raw_collected` after running the tests)
- parse pressure/meteorological files from different formats to a csv and apply a pressure correction based on altitude as input for a retrieval algorithm (see `examples/pressure`)

## Installation

Installation or syncing is best done with [Python Dependency Manager (PDM)](https://pdm-project.org/latest/), which should be installed in the system first.
These instructions are for installation with PDM.

A virtual environment can be created first, e.g. with conda (python >= 3.11), or let PDM handle the virtual environment (see PDM docs for more info).
If you have your own virtual environment, first tell PDM where it is:
```
pdm use </path/to/your/environment>
```

> 💡 Get a list of environments and their paths with `conda env list` if using conda.

You should now have a file in the directory called `.pdm-python` which contains the file path for your designated virtual environment for that submodule.
This tells PMD where to install packages.

Install with:
```
pdm sync --group dev --clean
```
> The `--clean` flag removes installed packages if they are no longer needed

Check the installation:
```
# activate your venv, e.g. if using conda:
conda activate <venv name>
pip freeze
```

or
```
ls -al /path/to/venv/lib/<python.version>/site-packages
```

You should see a list of all the packages listed in `pyproject.toml`

> Hint: if the installation didn't work, make sure that the path in `.pdm-python` points to the right directory.


## Test the installation by running tests with `pytest`

Activate the respective python virtual environment before running the tests, e.g. with conda:
```
conda activate <venv name>
```

To run the main tests, run:
```
make test-all
```

or, to test the environment is set up and the configuration file exists, run:
```
make test-integration
```

> A Makefile is used to set up the necessary files for the tests.

🔷 Before running the integration tests, make sure to set up the config file and export an environment variable pointing to it:
```
export PIPELINE_CONFIG_FILE=/path/to/config.yml
# check that it is set with
echo $PIPELINE_CONFIG_FILE
```
or set this variable in `.env`, e.g.:
```
cp -v .env.template .env
# update PIPELINE_CONFIG_FILE=/path/to/config.yml
```

## Configuration

Configure these tools via a YAML file.
An annotated example can be found at: `examples/example_pipeline_config.yml`.
A template can be found at `pipeline_config.template.yml`.
To skip a job or a section, comment out or delete the lines.

The following instructions assume the use case of moving an EM27/SUN instrument to a new location, although these tools can be used for more general use cases.

### Preparing symlinks for a new location

The `symlinks` section contains jobs for producing symlinks to pressure and interferogram folders/files.
Each job contains one link folder and multiple target folders:
```
target_folders:
  - "/full/path/to/target/folder/1"
  - "/full/path/to/target/folder/2"
link_folder: "/full/path/to/link/folder"
```

> 💡 Interferogram jobs use additional logic to parse measurement folder names (dates) into a format accepted by [em27-retrieval-pipeline](https://github.com/tum-esm/em27-retrieval-pipeline) (i.e. `yyyymmdd`).

From inside the virtual environment, run the symlink jobs with:
```
python -m modules.pipeline prepare_symlinks
```

#### Pressure symlink jobs

A new job needs to be set up (along with possible code adjustments) if a new pressure station provides files that are split up into multiple sub-folders to link them into a single folder for further processing with these tools.
Use a meaningful name for the job name (at the time of writing there is no logic that depends on the name of the job unless it is an interferogram symlinks job).

#### Interferogram symlink jobs

A new job needs to be set up if a new instrument is set up with the name `SNXXX` (the serial number), along with possible code adjustments: note that instrument serial numbers are hard coded into `pipeline.py` at the time of writing.
To use [em27-retrieval-pipeline](https://github.com/tum-esm/em27-retrieval-pipeline), if interferograms are split up, e.g. by location, all measurement directories of an instrument should be linked into a single directory, namely of the form `ifg-measurements/SNXXX/`.

### Preparing pressure files for retrievals

The `pressure` section contains jobs named after measurement locations.

Preparing pressure files involves two things:
- Parse measurements into a standard file format
- Apply a pressure correction to the measurements based on the altitude difference from the pressure sensor and the EM27/SUN mirrors.

When a new measurement location is created, regardless if the instrument is new or moved, the following should be done:
1. A job is added to the `pressure` section with the name of that interferogram measurement location (do not use the same location name more than once in this file).
2. Fill out the required fields:
    - `raw_pressure_folder`: where the raw pressure measurements are stored (this directory should not contain sub-directories; if raw pressure measurements are stored in a sub-directory structure, first use a [symlink job](#pressure-symlink-jobs), where `link_folder` will have the same value)
    - `raw_file_extension`: the extension of the raw pressure files for this location (note: typical pressure file extensions and formats are hard-coded at the time of writing; for new types of files, update the code as necessary)
    - `parsed_pressure_folder`: the location which will be referenced in the retrieval pipeline for the pressure for this location (the final directory in the path should be named after the location, e.g. `prepared-input-data/pressure/parsed-pressure-files/LOCATION_A`, and does not need to exist)
    - `start_date`: the first date for which pressure files should be processed (this can be e.g. the date the instrument started measuring in this location)
    - `end_date`: optional, default is yesterday
3. For creating a calibrated pressure column, configure the following fields:
    - `use_pressure_correction_factor`: set to True
    - `em27_m`: the elevation above sea level of the mirrors of em27 instrument in meters
    - `pressure_sensor_m`: the elevation above sea level of the pressure sensor in meters

> ⚠️ Note: use a period for decimal for numerical values when filling out this file.

From inside the virtual environment, run the pressure jobs with:
```
python -m modules.pipeline prepare_pressure
```

## Contributing

Contributions are warmly welcomed: open or solve an [issue](https://github.com/cfleur/automasun/issues) and create a pull request from your fork!