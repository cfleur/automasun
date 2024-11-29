from io import StringIO
from pathlib import Path
from typing import Generator, Tuple

import numpy as np
import pandas as pd
import pytest

from ..modules import pressureutils
from .fixtures import (
    mock_config_existing_processed_files,
    mock_config_no_processed_files,
    mock_processed_file_paths,
    CONF_SECTION_PRESSURE,
    LOCS,
    EXAMPLE_RAW_FILE_PATHS,
    EXAMPLE_PROCESSED_FILE_PATHS
)


def test_parse_pressure_folder(
        mock_config_no_processed_files: Path,
        mock_processed_file_paths: Tuple[Path, Path]
) -> None:
    for i, loc in enumerate(LOCS):
        pressureutils.parse_pressure_folder(
            mock_config_no_processed_files,
            CONF_SECTION_PRESSURE,
            loc
        )
        assert mock_processed_file_paths[i].exists()
    # TODO: check that function actually finds the files
    # and parses them, e.g. by tracking number of files found and parsed
    # in respective functions
    # currently, making tests fail (e.g. assert 0) shows print out from
    # from parse_pressure_folder which fails quietly with try-except block


def test_parse_pressure_file(
        tmp_path: Generator[Path, None, None]
) -> None:
    # Test that the content of parsed pressure file is correct
    for i, raw_input_path in enumerate(EXAMPLE_RAW_FILE_PATHS):
        mock_output_path: Path = tmp_path/f'tmp_parsed_loc{i}.csv'
        mock_output_path.touch()
        pressureutils.parse_pressure_file(
            raw_input_path,
            mock_output_path
        )
        mock_output_content = mock_output_path.read_text()
        with open(
            EXAMPLE_PROCESSED_FILE_PATHS[i],
            'r',
            encoding='utf-8'
        ) as f:
            example_output_content = f.read()
        assert mock_output_content == example_output_content


def test_apply_pressure_correction() -> None:
    vector = pd.Series([1,2,3,4], dtype=np.float64)
    correction_constant = 0.1
    correction_vector = [1,1,1,1]
    # Constant correction applied
    assert list(pressureutils.apply_pressure_correction(
        vector,
        correction_constant
    )) == [1.1,2.1,3.1,4.1]
    # Vector correction applied
    assert list(pressureutils.apply_pressure_correction(
        vector,
        correction_vector
    )) == [2,3,4,5]
    # No correction applied
    assert list(pressureutils.apply_pressure_correction(
        vector
    )) == list(vector)
    # Test that only accepts a pandas Series
    with pytest.raises(TypeError):
        pressureutils.apply_pressure_correction([1,2,3])
    # Test that vector correction should be correct length
    with pytest.raises(ValueError):
        pressureutils.apply_pressure_correction(
            vector,
            [1,2,3]
        )


def test_calculate_pressure_correction() -> None:
    barometric_factors = [0, 1, 25.1]
    reference_pressure = 10001.0
    results = [0, reference_pressure, reference_pressure*25.1]
    for B, r in zip(barometric_factors, results):
        np.testing.assert_almost_equal(
            pressureutils.calculate_pressure_correction(
                reference_pressure, B
            ),
            r
        )


def test_calculate_barometric_factor() -> None:
    h = 202.5
    h_b_vec = [202.5, 201.5, 200.0]
    # Math: h-h = 0, \quad h-201.5 \approx 1, \quad h-200.0 \approx 2.5
    g_0 = 9.80665
    M = 0.289644
    R = 8.314462
    T_K = 0 + 273.15
    results = [
        np.exp(-0/(R*T_K)),
        np.exp(-(g_0*M)/(R*T_K)),
        np.exp(-(g_0*M*(h-200.0))/(R*T_K))
    ]
    for h_b, r in zip(h_b_vec, results):
        np.testing.assert_almost_equal(
            pressureutils.calculate_barometric_factor(
                calculated_pressure_height = h, 
                reference_pressure_height = h_b,
                reference_temperature_C = 0
            ),
            r
        )


def test_generate_unparsed_pressure_file_list(
        mock_config_no_processed_files: Path,
        mock_config_existing_processed_files: Path,
        mock_processed_file_paths: Tuple[Path, Path]
) -> None:
    # Test that when there are no matching processed and raw dates,
    # correct output paths are created for both file types
    for i, loc in enumerate(LOCS):
        unparsed_paths, output_paths = pressureutils.generate_unparsed_pressure_file_list(
            mock_config_no_processed_files,
            CONF_SECTION_PRESSURE,
            loc
        )
        assert unparsed_paths == [EXAMPLE_RAW_FILE_PATHS[i]]
        assert output_paths == [mock_processed_file_paths[i]]
    # Test that when there are already processed files for
    # the same dates as raw files, the output is empty
    for loc in LOCS:
        unparsed_paths, output_paths = pressureutils.generate_unparsed_pressure_file_list(
            mock_config_existing_processed_files,
            CONF_SECTION_PRESSURE,
            loc
        )
        assert (unparsed_paths, output_paths) == ([], [])


def test_preprocess_case_log_file(
        tmp_path: Generator[Path, None, None]
) -> None:
    content: str = '='
    file: Path = tmp_path/'tmp_raw_file.txt'
    file.write_text(content)
    preprocessed_file: StringIO = pressureutils.preprocess_case_log_file(
        file
    )
    assert preprocessed_file.read() == ' '
