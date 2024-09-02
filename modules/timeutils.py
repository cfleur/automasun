import numpy as np
import pandas as pd

from datetime import datetime, timedelta


def epoch_to_date(time_data, epoch_start_date):
    datetimes = []

    for time in time_data:
        time_diff = timedelta(days=time)
        datetimes.append(epoch_start_date + time_diff)
    
    return datetimes

def date_to_epoch(time_data, epoch_start_date):
    epochtimes = []

    for time in time_data:
        time_diff = time - epoch_start_date
        epoch_time = np.float64(time_diff.days + (time_diff.seconds/(3600*24)))
        epochtimes.append(epoch_time)

    return epochtimes


def datestring_to_datetime(datestring_array):
    datetime_array = []

    for ds in datestring_array:
        datetime_array.append(datetime.strptime(ds, "%Y-%m-%d %H:%M:%S"))

    return datetime_array


def datetime_to_clocktime(datetime_array):
    # FIXME: this only works for unique times for one day
    clocktime_array = []
    
    for dt in datetime_array:
        minute = dt.minute if len(str(dt.minute)) > 1 else '0' + str(dt.minute)    # add a 0 to single digit minutes
        second = dt.second if len(str(dt.second)) > 1 else '0' + str(dt.second)    # add a 0 to single digit minutes
        clocktime_array.append(f'{dt.hour}:{minute}:{second}')
    
    return clocktime_array


def timestamp_to_date_time(
        timestamps: list,
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
        _date.append(str(ts_items[0]))
        _time.append(str(ts_items[1]))

    return pd.DataFrame(np.array([_date, _time]).T, columns=['date','time'])