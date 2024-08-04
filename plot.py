import matplotlib.pyplot as plt
import numpy as np

import timeutils


def compare_all_timestamps(timeseries: dict,
                           disagreeing_timestamps: dict,
                           epoch_start_date, 
                           title: str = '',
                           y_series_name: str = '',
                           y_test_offset: float = 0.0033, 
                           full_file_path: str = '') -> None:
    """
    Plots two time series and adds vertical lines where there are disagreeing timestamps
    in the series. Plots times of the day on the x axis. X axis data should be in epoch times.

    Keyword arguements:
    timeseries = {'epochtime_test', 'y_test', 'epochtime_ref', 'y_ref'}
    disagreeing_timestamps = {'test', 'ref'}
    """
    
    fig, ax = plt.subplots(figsize=(16,8))
    fig.patch.set_facecolor('silver')
    ax.patch.set_facecolor('silver')
    
    ax.set_title(title)
    ax.set_ylabel(y_series_name)
    ax.set_xlabel(f'epoch time since {epoch_start_date}\nclock time')

    # labels for disagreeing timestamps
    ax.plot([],[], color='darkred', linewidth=0.7, alpha=0.5, linestyle='dashed',
            label='extra measurement local data')
    ax.plot([],[], color='darkgreen', linewidth=1.7, alpha=0.5, linestyle='dotted',
            label='extra measurement reference data')

    # data series test
    ax.plot(timeseries['epochtime_test'], timeseries['y_test'] + y_test_offset, '-',
            color='darkorange', alpha=0.5,
            label=f'local data{y_series_name} + {y_test_offset}')
    
    # data series ref
    ax.plot(timeseries['epochtime_ref'], timeseries['y_ref'],
            color='darkblue', alpha=0.5,
            label=f'COCCON data repo {y_series_name}')

    # vertical lines at extra times in ref data
    for et in disagreeing_timestamps['ref']:
        ax.axvline(x=et, color='darkgreen', linewidth=1.7, alpha=0.5, linestyle='dotted')

    # vertical lines at extra times in test data
    for et in disagreeing_timestamps['test']:
        ax.axvline(x=et, color='darkred', linewidth=0.7, alpha=0.5, linestyle='dashed')
    
    # tick, tick labels and grid
    major_tick_spacing = 0.03
    minor_tick_scale_factor = 0.1
    major_ticks = np.arange(np.min(timeseries['epochtime_test']), np.max(timeseries['epochtime_test']), major_tick_spacing)
    minor_ticks = np.arange(np.min(timeseries['epochtime_test']), np.max(timeseries['epochtime_test']), major_tick_spacing*minor_tick_scale_factor)
    tick_clocktime_labels = timeutils.datetime_to_clocktime(timeutils.epoch_to_date(major_ticks, epoch_start_date))
    x_lab_string = [str(t)+f'\n{s}' for t, s in zip(np.round(major_ticks, 3), tick_clocktime_labels)]
    ax.set_xticks(major_ticks, labels=x_lab_string)
    ax.set_xticks(minor_ticks, minor=True)
    ax.grid(color='black', alpha=0.20, which='major')
    ax.grid(color='black', alpha=0.08, which='minor')

    # legend
    ax.legend(framealpha=0)

    plt.show()
    
    if len(full_file_path) > 0:
        fig.savefig(full_file_path)