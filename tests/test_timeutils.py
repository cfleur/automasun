import numpy as np
import pandas as pd

from ..modules import timeutils


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
