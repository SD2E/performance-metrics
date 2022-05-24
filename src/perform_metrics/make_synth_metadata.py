"""
code to make synethetic metadata

:author: Tessa Johnson (tessa.johnson@geomdata.com)
:copyright: (c) 2020, Geometric Data Analytics, Inc.
:license: , see LICENSE for more details
"""

import pandas as pd
import numpy as np
import itertools
import argparse
import os


def make_synth_metadata():
    """
    makes a synthetic metadata set

    for configuration:
    observed_output_col = 'observed_fluor'
    intended_output_col = 'intended_output'
    intended_output_col_on = '1'
    intended_output_col_off = '0'

    'exp_str': ['experiment_id', 'strain'],
    'exp_str_ts': ['experiment_id', 'strain', 'output_id'],
    'exp_str_ts_rep': ['experiment_id', 'strain', 'output_id', 'replicate']

    pandas.DataFrame, columns: ['experiment_id', 'output_id', 'time', 'replicate', 'intended_output',
       'input', 'sample_id']
    """
    # make up some time series input/output patterns
    times = [1, 2, 3]
    ts_io = {
        'ts1': {'i': ['01', '00', '00'],
                'o': ['0', '1', '1']},
        'ts2': {'i': ['00', '01', '01'],
                'o': ['1', '0', '0']}}

    details = {
        'experiment_id': ['exp1', 'exp2'],  # this is a group of time series?
        'strain': ['UWBF1', 'UWBF2'],  # this is the circuit
        'output_id': ['ts1', 'ts2'],  # this is one time series?
        'time': times,
        'replicate': [1, 2, 3, 4, 5],
    }

    keys, values = zip(*details.items())
    records = [dict(zip(keys, x)) for x in itertools.product(*values, repeat=1)]

    # make some clean 0 = low and 1 = high records, low noise.
    for i, record in enumerate(records):
        record['input'] = ts_io[record['output_id']]['i'][times.index(record['time'])]
        record['intended_output'] = ts_io[record['output_id']]['o'][times.index(record['time'])]
        record['sample_id'] = i

    data_df = pd.DataFrame(records)

    return data_df


def make_synth_data():
    """
    makes a synthetic data set in a narrow format. synthetic data is plate reader data.


    :return: pandas.DataFrame, columns: ['observed_fluor', 'sample_id']

    """
    # make up some time series input/output patterns
    times = [1, 2, 3]
    ts_io = {
        'ts1': {'i': ['01', '00', '00'],
                'o': ['0', '1', '1']},
        'ts2': {'i': ['00', '01', '01'],
                'o': ['1', '0', '0']}}

    details = {
        'experiment_id': ['exp1', 'exp2'],  # this is a group of time series?
        'strain': ['UWBF1', 'UWBF2'],  # this is the circuit
        'output_id': ['ts1', 'ts2'],  # this is one time series?
        'time': times,
        'replicate': [1, 2, 3, 4, 5],
    }

    keys, values = zip(*details.items())
    # keep this so it properly aligns with metadata
    meta_records = [dict(zip(keys, x)) for x in itertools.product(*values, repeat=1)]
    records = []

    # make some clean 0 = low and 1 = high records, low noise.
    for i, mrecord in enumerate(meta_records):
        record = {}
        intended_output = ts_io[mrecord['output_id']]['o'][times.index(mrecord['time'])]
        record['sample_id'] = i
        if intended_output == '0':
            mu, sigma = 100, 25
        else:
            mu, sigma = 1000, 250
        observed_fluor = np.random.normal(mu, sigma, 1)[0]
        record.update({'observed_fluor': observed_fluor})
        records.append(record)

    data_df = pd.DataFrame(records)

    return data_df


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("output_path", help="output_path")
    args = parser.parse_args()
    output_path = args.output_path
    
    metadta = make_synth_metadata()
    dta = make_synth_data()
    
    output_meta_data_path = os.path.join(output_path, "synthetic_metadata.csv")
    output_data_path = os.path.join(output_path, "synthetic_data_output_only.csv")
    
    metadta.to_csv(output_meta_data_path, index=False)
    dta.to_csv(output_data_path, index=False)
