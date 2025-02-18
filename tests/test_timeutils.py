from contextlib import nullcontext
import datetime as dt

import numpy as np
import pandas as pd
import pytest

from modules import timeutils


# @pytest.mark.only
@pytest.mark.parametrize(
        "input_date, start_date, end_date, expectation",
        [
            pytest.param(
                dt.date(2000, 1, 13), dt.date(1990, 1, 13), dt.date(2025, 1, 13), nullcontext(True), id="date-in-range"
                ),
            pytest.param(
                dt.date(1, 1, 1), dt.date(1990, 1, 13), dt.date(2025, 1, 13), nullcontext(False), id="date-too-early"
                ),
            pytest.param(
                dt.date(3000, 1, 13), dt.date(1990, 1, 13), dt.date(2025, 1, 13), nullcontext(False), id="date-too-late"
                ),
            pytest.param(
                dt.date(2000, 1, 13), dt.date(3000, 1, 13), dt.date(2025, 1, 13), pytest.raises(ValueError), id="bad-range"
                )
        ]
)
def test_date_in_range(
        input_date,
        start_date,
        end_date,
        expectation
) -> None:
    with expectation as e:
        assert timeutils.date_in_range(
            input_date,
            start_date,
            end_date,
        ) == e


# @pytest.mark.only
def test_format_datestring() -> None:
    original_date: str = "01.09.2021"
    original_format: str = "%d.%m.%Y"
    desired_format: str = "%Y-%m-%d"
    desired_output: str = "2021-09-01"
    assert timeutils.format_datestring(
        original_date,
        original_format,
        desired_format
    ) == desired_output


# @pytest.mark.only
def test_timestamp_to_date_time() -> None:
    timestamps = ["2016-06-02 18:00"]
    sep = " "
    df = pd.DataFrame(
        np.array([
            ["2016.06.02"],
            ["18:00:00"]
        ]).T,
        columns = [
            'date',
            'time'
        ]
    )
    assert timeutils.timestamp_to_date_time(
        timestamps,
        sep
    ).equals(df)
