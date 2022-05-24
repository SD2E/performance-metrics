"""
code for calculating the group metrics for ON vs OFF states

:author: Anastasia Deckard (anastasia.deckard@geomdata.com), Tessa Johnson (tessa.johnson@geomdata.com)
:copyright: (c) 2020, Geometric Data Analytics, Inc.
:license: , see LICENSE for more details
"""

import numpy as np
from collections import OrderedDict


def compute_metric_percent(on, off):
    """
    treat the ON and OFF states as distributions, and compare their percentiles
    for specified grouping of columns (exp, ts, etc)

    for the OFF, use q to get right hand side of dist; for ON, use 1 - q to get left hand side of dist
    median if q = 50,  minimum if q = 0, maximum if q = 100.

    :param on: data associated with the ON state
    :param off: data associated with the OFF state
    :return: dictionary of data associated with percentile metric
    """
    # percents to use
    # for the OFF, use q to get right hand side of dist; for ON, use 1 - q to get left hand side of dist
    # median if q = 50,  minimum if q = 0, maximum if q = 100.
    percents = [100, 75, 50]
    records = list()

    for percent in percents:
        # compute absolute difference
        # check to make sure list exists
        if len(off) > 0:
            off_agg = np.nanpercentile(off, percent)
        else:
            off_agg = np.nan
        if len(on) > 0:
            on_agg = np.nanpercentile(on, 100 - percent)
        else:
            on_agg = np.nan

        diff = on_agg - off_agg
        ratio = on_agg / off_agg  # need to catch zero here

        # make record
        record = OrderedDict()
        record['percentile'] = percent
        record['off_agg'] = off_agg
        record['on_agg'] = on_agg
        record['diff'] = diff
        record['ratio'] = ratio

        records.append(record)

    return records


def compute_metric_sd(on, off):
    """
    computing the difference between mean +/- SD to detect change difference between ON vs OFF states
    :param on: data associated with the ON state
    :param off: data associated with the OFF state
    :return: dictionary of values associated with sd metric
    """

    num_std = [0, 1, 2, 3]

    # group by the exp and ts ids
    records = list()
    for n_std in num_std:
        if len(off) > 0:
            off_agg = np.nanmean(off) + (np.nanstd(off) * n_std)
        else:
            off_agg = np.nan
        if len(on) > 0:
            on_agg = np.nanmean(on) - (np.nanstd(on) * n_std)
        else:
            on_agg = np.nan
        diff = on_agg - off_agg
        ratio = on_agg / off_agg

        # make record
        record = OrderedDict()
        record['num_std'] = n_std
        record['off_agg'] = off_agg
        record['on_agg'] = on_agg
        record['diff'] = diff
        record['ratio'] = ratio

        records.append(record)

    return records


# Dictionary associated with each metric, users can append to the dictionary to add more metrics
metrics_info = [
        {'metric': 'perc',
         'function': compute_metric_percent,
         'file_name': 'metrics_per_',
         'comments': "# percentiles difference \n"
                     "# OFF, use q to get right hand side of dist; "
                     " ON, use 1 - q to get left hand side of dist "
                     "median if q = 50,  minimum if q = 0, maximum if q = 100.\n"
                     "# grouped by:'",
         "plot_metric": ('percentile', 50)},

        {'metric': 'sd',
         'function': compute_metric_sd,
         'file_name': 'metrics_sd_',
         'comments': "# mean +/- SD intervals \n"
                     "# off_minus_on = (mean_off + std_off) - (mean_on - std_on)"
                     "on_minus_off = (mean_on + std_on) - (mean_off - std_off)\n"
                     "# grouped by:'",
         "plot_metric": ('num_std', 0)}
    ]
