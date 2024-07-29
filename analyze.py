import pandas as pd
pd.set_option('display.max_colwidth', 100)

import numpy as np
import datetime

import read
import timeutils
import plot

# TODO: remove module reloads when done
import importlib
importlib.reload(plot)
importlib.reload(timeutils)
importlib.reload(read)

def print_csv_h5_keys(path, sep=',') -> None:
    file_type = str.split(path, '.')[-1]

    if file_type == 'csv':
        # TODO: include option to change separator
        print(pd.DataFrame(read.csv_get_keys(path, sep=sep)))
        
    if file_type == 'h5':
        print(pd.DataFrame(read.h5_get_keys(path)))


def show_keys(
        file_paths: any,
        sep=',',
        ) -> None:
    """
    """ 

    if type(file_paths) == list:
        for path in file_paths:
            print_csv_h5_keys(path, sep=sep)

    elif type(file_paths) == str:
        print_csv_h5_keys(file_paths, sep=sep)
    
    elif  type(file_paths) == dict:
        for key in file_paths.keys():
            print_csv_h5_keys(file_paths[key], sep=sep)
    else:
        print('Supplied filepaths must be of str, list or dict type.')
        raise(TypeError)
    
def compare_single_day(
        filepaths: dict,
        col_numbers: dict
        ) -> None:
    """
    Keyword args:

    filepaths = {'test', 'ref'}
    col_numbers = {'data_test', 'time_test', 'data_ref', 'time_ref'}
    """ 

    f_test = filepaths['test']
    f_ref = filepaths['ref']

    # Read in reference and test datasets

    # CH4 column
    data_test = np.array(read.csv_get_col(f_test, col_numbers['data_test']))
    data_ref = np.array(read.h5_get_col(f_ref, col_numbers['data_ref']))

    # Time column
    data_test_time = np.array(read.csv_get_col(f_test, col_numbers['time_test']))
    data_ref_time = np.array(read.h5_get_col(f_ref, col_numbers['time_ref']))

    # Parse time columns
    epoch_start_date = datetime.datetime(2000, 1, 1)

    # Create epoch time arrays for the x axis
    epochtime_ref = data_ref_time
    epochtime_test = timeutils.date_to_epoch(timeutils.datestring_to_datetime(data_test_time), epoch_start_date)

    # Extract disagreeing timestamps

    # convert epoch and string times to "clock time" for set difference operation on strings
    # FIXME: this could also be done directly with the date strings that come with the retrieval result csv
    clocktime_ref = timeutils.datetime_to_clocktime(timeutils.epoch_to_date(data_ref_time, epoch_start_date))
    clocktime_test = timeutils.datetime_to_clocktime(timeutils.datestring_to_datetime(data_test_time))

    # set subtraction to get elements that are NOT in both sets
    # this works with sets of strings but not floating point numbers
    # hence the epoch times are converted to clock time strings
    extra_clocktimes_ref = set(clocktime_ref) - set(clocktime_test)
    extra_clocktimes_test = set(clocktime_test) - set(clocktime_ref)

    # index of disagreeing timestamps
    extra_index_ref = [clocktime_ref.index(i) for i in extra_clocktimes_ref]
    extra_index_test = [clocktime_test.index(i) for i in extra_clocktimes_test]

    # get epoch time stamp at disagreeing indices to a list
    # caveat: all time lists should be in the same order
    extra_epochtimes_ref = [epochtime_ref[i] for i in extra_index_ref]
    extra_epochtimes_test = [epochtime_test[i] for i in extra_index_test]

    # Assemble datasets for plotting
    timeseries = {
        'epochtime_test': epochtime_test, 
        'y_test': data_test,
        'epochtime_ref': epochtime_ref,
        'y_ref': data_ref
        }

    disagreeing_timestamps = {
        'test': extra_epochtimes_test,
        'ref': extra_epochtimes_ref
        }

    # plot
    title = 'PROFFASTPylot processing results comparison\n \
                    Sodankylä EM27SUN SN122 01-06-2020 ~07:00-13:00 UTC\n \
                    Scalar pressure offest of -0.29650 applied'
    plot.compare_all_timestamps(timeseries, disagreeing_timestamps, epoch_start_date, title, 'XCH4') 
