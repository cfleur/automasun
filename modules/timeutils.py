import datetime as dt

import numpy as np
import pandas as pd


def date_in_range(
        input_date: dt.date,
        start_date: dt.date,
        end_date: dt.date
) -> bool:
    """
    Checks if a date is equal or later than start_date,
    and equal or earlier than end_date.
    """
    if start_date > end_date:
        raise ValueError(
            f"start_date {start_date} must be earlier or equal to end_date {end_date}."
        )
    return input_date >= start_date and input_date <= end_date


def format_datestring(
        original_date: str,
        original_format: str,
        desired_format: str
) -> str:
    """
    Transforms a date string into another date string with different formatting

    Parameters
    ----------
    original_datestring : str,
        the original date, e.g. "01.09.2021"
    original_format : str,
        the format of the original date, e.g. "%d.%m.%Y"
    desired_format : str
        the format of the desired date, e.g. "%Y-%m-%d"

    Returns
    -------
    str
        e.g. "2021-09-01"
    """
    d = dt.datetime.strptime(
        original_date,
        original_format
    )
    return d.strftime(
        desired_format
    )


def timestamp_to_date_time(
        timestamps: list[str],
        sep: str = ' '
        ) -> pd.DataFrame:
    """Takes a list of timestamps and returns a 
    DataFrame with date and time columns.

    Parameters
    ----------
    timestamps : list like
        list of timestamps to parse
    sep : str
        separator of date and time

    Returns
    -------
    pd.DataFrame
        =====  ===========
        date   str 
        time   str 
        =====  ===========
    """
    _date = []
    _time = []
    for ts in timestamps:
        ts_items = ts.split(sep)
        d = str(
            ts_items[0]
        ).split('-')
        # date format: yyyy.mm.dd
        _date.append(
            f'{d[0]}.{d[1]}.{d[2]}'
        )
        # time format: hh:mm:ss
        # 00 added as granularity is in minutes for this data
        _time.append(
            f'{str(ts_items[1])}:00'
        )
    return pd.DataFrame(
        np.array([
            _date,
             _time
        ]).T,
        columns=[
            'date',
            'time'
        ]
    )
