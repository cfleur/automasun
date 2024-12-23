from datetime import datetime, timedelta
from io import StringIO
from pathlib import PosixPath, Path
from typing import List, Tuple, Union

import pandas as pd
import numpy as np

from . import ioutils
from . import timeutils


def parse_pressure_folder(
        config_file: Union[str, PosixPath],
        pressure_config_section: str,
        location: str,
        v: bool = False,
        vv: bool = False
) -> None:
    """
    Parses all unparsed pressure files in a folder. Output is written to output folder
    defined in yaml config file.
    """
    unparsed_pressure_paths, output_paths = generate_unparsed_pressure_file_list(
        config_file,
        pressure_config_section,
        location,
        v=v, vv=vv
    )
    print(
        f'******\nFound {len(unparsed_pressure_paths)} unparsed pressure files'
        f' for location « {location} ».\n**'
    )
    pressure_correction = calculate_barometric_factor(
        get_elevations(
            config_file,
            pressure_config_section,
            location,
            v=v
        )
    )
    file_count = 0
    for in_path, out_path in zip(unparsed_pressure_paths, output_paths):
        try:
            parse_pressure_file(
                in_path,
                out_path,
                pressure_correction,
                'factor',
                v=v
            )
            file_count += 1
        except Exception as exc:
            # TODO: create better error handling (not enough printout for errors, too general exception)
            print(
                f"* Failed to parse {in_path}:\n",
                exc
            )
    print(
        f'**\nParsed {file_count} pressure files for location « {location} ».\n******'
    )


def parse_pressure_file(
        input_file_path: Union[str, PosixPath],
        output_file_path: Union[str, PosixPath],
        pressure_correction: Union[None, float, list] = None,
        pressure_correction_type: str = 'factor',
        in_sep: Union[None, str] = None,
        out_sep: str =',',
        in_col_names: Union[None, dict] = None,
        out_col_names: Union[None, dict] = None,
        v: bool = False,
        q: bool = False
) -> None:
    """Takes aws .lst or .txt log pressure file as input and
    creates a .csv file with data necessary for retrieval algorithm.
    """
    if v:
        print('*'*4,'Creating formatted pressure file.')
    # set default values for mutable type arguments
    if in_col_names is None:
        in_col_names = {}
    if out_col_names is None:
        out_col_names = {
            'date': 'Date',
            'time': 'TimeUTC',
            'pressure': 'PressureBaroTHB40',
            'correction': 'CalibrationFactor',
            'corrected_p': 'CalibratedPressurehPa',
            'temperature': 'TemperatureC',
            'rh': 'RelativeHumidity'
        }
    input_file_type = ioutils.get_file_extension(input_file_path)
    if input_file_type == 'lst':    # automatic weather station (aws) file
        if in_sep is None:
            in_sep = r'\s\s+'
        df = pd.read_csv(input_file_path, sep=in_sep, engine='python').drop(0)

        # parse timestamp
        if 'timestamp_col_name' in in_col_names:
            timestamp_col_name = in_col_names['timestamp_col_name']
        else:
            timestamp_col_name = df.columns[0]
        timestamps = list(df[timestamp_col_name])
        timestamp_df = timeutils.timestamp_to_date_time(timestamps)
        _pressure = df['P_ST']
        _correction, _corrected_pressure = apply_pressure_correction(
            pressure_vector=_pressure,
            pressure_correction=pressure_correction,
            pressure_correction_type=pressure_correction_type,
            q=q
        )
        _temperature = df['T']
        _relative_humidity = df['RH']
        _out_pressure = pd.DataFrame(
            np.array([
                timestamp_df['date'],
                timestamp_df['time'],
                _pressure,
                np.full(
                    _pressure.shape,
                    _correction
                ),
                _corrected_pressure,
                _temperature,
                _relative_humidity
            ]).T,
            columns=[
                out_col_names['date'],
                out_col_names['time'],
                out_col_names['pressure'],
                out_col_names['correction'],
                out_col_names['corrected_p'],
                out_col_names['temperature'],
                out_col_names['rh']
            ])
    elif input_file_type == 'txt':  # em27 case log file
        if in_sep is None:
            in_sep = r'\s+'
        df = pd.read_csv(
            preprocess_case_log_file(
                input_file_path
            ),
            sep=in_sep,
            engine='python',
            skiprows=2,
            header=None
        )
        _pressure = df[9]
        _correction, _corrected_pressure = apply_pressure_correction(
            pressure_vector=_pressure,
            pressure_correction=pressure_correction,
            pressure_correction_type=pressure_correction_type,
            q=q
        )
        _date = [
                    timeutils.format_datestring(
                        original_date = d,
                        original_format = "%d.%m.%Y",
                        desired_format = "%Y.%m.%d"
                    )
                    for d in df[0]
                ]
        _out_pressure = pd.DataFrame(
            np.array([
                _date,
                df[1],
                _pressure,
                np.full(
                    _pressure.shape,
                    _correction
                ),
                _corrected_pressure,
                df[12],
                df[15]
            ]).T,
            columns=[
                out_col_names['date'],
                out_col_names['time'],
                out_col_names['pressure'],
                out_col_names['correction'],
                out_col_names['corrected_p'],
                out_col_names['temperature'],
                out_col_names['rh']
            ])
    else:
        raise ValueError(
            f"Supported input file types: '.lst', '.txt'."
            f" Got '{input_file_type}'."
        )
    output_dir = Path(output_file_path).parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    print(output_file_path)
    _out_pressure.to_csv(output_file_path, index=False, sep=out_sep)
    if not q:
        print(f'{output_file_path.name} pressure file written {datetime.now().time()}.')
    if v:
        print(f'Pressure file location: {output_file_path}')


def apply_pressure_correction(
        pressure_vector: pd.Series,
        pressure_correction: Union[None, float, list] = None,
        pressure_correction_type: str = 'factor',
        q: bool = False
) -> Tuple[Union[None, float, list], pd.Series]:
    """
    Applies a pressure correction. Correction can either be a constant or an array or None.
    If correction is none, input vector is returned unchanged.

    Parameters:
    ----------
    pressure_vector: pandas Series
        Pressures to correct.
    pressure_correction: None | float | list like
        Value(s) to apply as pressure correction (None means no correction).
        Default is None.
    pressure_correction_type: str
        Whether to apply the correction as an offset (addition) or a factor (multiplication).
        Default is 'offset'.
    q: bool
        Quiet; suppress printed output.

    Returns:
    -------
    pandas Series
        Corrected pressure vector
    """
    if not isinstance(
        pressure_vector, pd.Series
    ) or pressure_vector.dtype != np.float64:
        raise TypeError(
            'Input pressure vector should be a pandas series with dtype=numpy.float64.'
        )
    if pressure_correction_type not in ['offset', 'factor']:
        raise ValueError(
            "pressure_correction_type must be one of 'offset', 'factor'"
        )
    _vector = pressure_vector.copy(deep=True)
    if pressure_correction is None:
        if not q:
            print('No pressure correction applied.')
            return(
                pressure_correction,
                _vector
            )
    elif isinstance(pressure_correction, float):
        if pressure_correction_type == 'offset':
            if not q:
                print(
                    f'Scalar pressure offset of {pressure_correction:.9f} added.'
                )
            return(
                pressure_correction,
                _vector + pressure_correction
            )
        elif pressure_correction_type == 'factor':
            if not q:
                print(
                    f'Scalar pressure factor of {pressure_correction:.9f} multiplied.'
                )
            return(
                pressure_correction,
                _vector * pressure_correction
            )
    elif isinstance(
        pressure_correction, (list, np.ndarray, pd.Series)
    ) and len(pressure_correction) == len(_vector):
        if all(
            isinstance(
                x, (int, float)
            ) for x in pressure_correction
        ):
            if pressure_correction_type == 'offset':
                if not q:
                    print(
                        'Vector pressure offest added.'
                    )
                return(
                    pressure_correction,
                    _vector + pressure_correction
                )
            elif pressure_correction_type == 'factor':
                if not q:
                    print(
                        'Vector pressure factor multiplied.'
                    )
                return(
                    pressure_correction,
                    _vector * pressure_correction
                )
        else:
            raise ValueError(
                'All elements in pressure_correction must be numeric.'
            )
    else:
        raise ValueError(
            'Pressure correction must be either None (default), a float, or an array of'
            ' numeric values of the same length as the number of pressure measurements.'
        )


def calculate_barometric_factor(
        calculated_and_reference_elevations: Tuple[float, float] | None,
        reference_temperature_C: float = 20
) -> float:
    """
    Given a constant reference temperature, the exponential part of the
    barometric formula is calculated as a pressure correction factor.
    If None is the first argument, None is returned.

    Parameters
    ----------
    calculated_and_reference_elevations: (float, float) | None
        the elevation in m of the vertical position of the desired calculated pressure, h, and
        the elevation in m of the vertical position of the measured reference pressure, h_b
    reference_temperature_C: float,
        the temperature in degrees Celcius, T_C. Default value is 20 degrees C. The temperature should not vary between h and h_b
        to use this formula. The pressure calculation only have a weak dependency on temperature,
        e.g. from -20 to 20 C there is only about 0.035 Pa variance
        [online pressure calculator](https://www.omnicalculator.com/physics/air-pressure-at-altitude).

    The barometric formula further relies on several constants:
    R: float,
        the universal gas constant =  8.314462 J/(mol·K)
    g_0: float,
        gravitational acceleration = 9.80665 m/s2
    M: float,
        the molar mass of Earth's air = 0.0289644 kg/mol

    Returns
    -------
    pressure correction factor: float,
        calculated via the barometric formula:
        # Math:
            \hat{B} = exp(\frac{-g_0 M H}{R T_K}),
            where
        # Math:
            H = h-h_b
            and
        # Math:
            T_K = T_C + 273.15

    Note that the full barometric formula is:
    # Math:
        P = P_b \hat{B}
    Therefore applying this factor to a vector of pressure measurements, P_b,
    results in a vector of corrected pressure P.
    """
    if calculated_and_reference_elevations is None:
        return None
    g_0: float = 9.80665
    M: float = 0.289644
    H: float = calculated_and_reference_elevations[0] - calculated_and_reference_elevations[1]
    # Math: H = h-h_b
    R: float = 8.314462
    T_K: float = reference_temperature_C + 273.15
    return np.exp(
        -(g_0*M*H) / (R*T_K)
    )


def get_elevations(
        config_file: Union[str, PosixPath],
        pressure_config_section: str,
        location: str,
        v: bool = False,
) -> Tuple[float, float] | None:
    """
    Reads the config file and returns elevation difference between pressure sensor and em27 instrument.
    Elevation should be measured at the middle of the pressure sensor and at the mirrors of the em27 instrument.
    The difference is calculated:
    # Math:
        H = h-h_b,
    where h is the elevation of the em27 instrument and h_b is the elevation of the pressure sensor.
    """
    pressure_config = ioutils.read_yaml_config(config_file)[pressure_config_section]
    use_pressure_correction_factor = pressure_config[location]['use_pressure_correction_factor']
    if use_pressure_correction_factor is True:
        # make sure both pressure sensor and em27 values are given
        if any(
            elevation is None for elevation in (
                pressure_config[location]['pressure_sensor_m'],
                pressure_config[location]['em27_m']
            )
        ):
            raise ValueError(
                'To calculate a pressure calibration factor, ensure both'
                ' pressure sensor and em27 elevation values in m are provided'
                f' in pipeline configuration file for {location}.'
            )
        try:
            pressure_sensor_elevation_m: float = float(
                pressure_config[location]['pressure_sensor_m']
            )
            em27_elevation_m: float = float(
                pressure_config[location]['em27_m']
            )
        except (TypeError, ValueError):
            print(
                f'Could not convert elevations to float for {location}.'
                ' Check config file elevation data.'
            )
            raise
        # elevation_difference: float = em27_elevation_m - pressure_sensor_elevation_m
        # Math:   H = h-h_b,
        if v:
            print(
                f'Elevation information for {location}:'
                f'\nem27_m: {em27_elevation_m}'
                f'\npressure_sensor_m: {pressure_sensor_elevation_m}'
                # f'\nElevation difference: {elevation_difference}'
            )
        # return elevation_difference
        return em27_elevation_m, pressure_sensor_elevation_m
    elif use_pressure_correction_factor in (False, None):
        return None
    else:
        raise ValueError(
            'Config parameter use_pressure_correction_factor must be True, False or empty.'
            f' Got {use_pressure_correction_factor}.'
        )


def generate_unparsed_pressure_file_list(
        config_file: Union[str, PosixPath],
        pressure_config_section,
        location: str,
        v: bool = False,
        vv: bool = False
) -> Tuple[
        tuple[Path],
        tuple[Path]
    ]:
    """
    Takes raw and parsed pressure folders from a config file and
    compares the contents based on dates in the file names.
    Returns a list of full paths of unparsed pressure files.
    """
    pressure_config = ioutils.read_yaml_config(config_file)[pressure_config_section]
    raw_pressure_folder = pressure_config[location]['raw_pressure_folder']
    parsed_pressure_folder = pressure_config[location]['parsed_pressure_folder']
    start_date = datetime.strptime(
        pressure_config[location]['start_date'],
        "%Y-%m-%d"
    ).date()
    # Default end date is yesterday
    if pressure_config[location]['end_date'] is None:
        end_date = datetime.now().date() - timedelta(days=1)
    else:
        end_date = datetime.strptime(
            pressure_config[location]['end_date'],
            "%Y-%m-%d"
    ).date()
    raw_pressure_dates = ioutils.generate_date_list_from_folder(
        raw_pressure_folder,
        start_date=start_date,
        end_date=end_date,
        v=v,
        vv=vv
    )
    parsed_pressure_dates = ioutils.generate_date_list_from_folder(
        parsed_pressure_folder,
        start_date=start_date,
        end_date=end_date,
        v=v,
        vv=vv
    )
    unparsed_pressure_dates = ioutils.generate_set_difference(
        set(raw_pressure_dates),
        set(parsed_pressure_dates)
    )
    unparsed_pressure_files = ioutils.generate_file_list_from_dates(
        unparsed_pressure_dates,
        pressure_config[location]["raw_file_extension"]
    )
    output_file_names = ioutils.generate_file_list_from_dates(
        unparsed_pressure_dates,
        'csv',  # keep as "csv" to help keep COCCON processing same format
                # as parsed pressure files are sent to KIT
        location
    )
    unparsed_pressure_paths = tuple(
        Path(raw_pressure_folder)/file
        for file
        in unparsed_pressure_files
    )
    output_paths = tuple(
        Path(parsed_pressure_folder)/name
        for name
        in output_file_names
    )
    return unparsed_pressure_paths, output_paths


def preprocess_case_log_file(
        file_path: Union[str, PosixPath]
) -> StringIO:
    """
    Replaces equal signs in case log file to prevent double digit temperature
    readings from changing the number of columns in the file.
    Without preprocessing label and value are not separated by a space:
    T=-10
    With preprocessing label and value are separated by a space:
    T -10
    After preprocessing "-10" will be read into a dataframe as a numerical value for temperature.
    This preprocessing allows to sure pandas read_csv with separator r"\s+" (one or more spaces).
    Returns a StringIO object in order to avoid writing a partially processed pressure file.
    """
    with open(file_path, 'r') as file:
        data = file.read()
    return StringIO(data.replace('=', ' '))
