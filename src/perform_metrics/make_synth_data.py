"""
code to make synethetic data 

:author: Anastasia Deckard (anastasia.deckard@geomdata.com), Tessa Johnson (tessa.johnson@geomdata.com)
:copyright: (c) 2019, Geometric Data Analytics, Inc.
:license: , see LICENSE for more details
"""

import pandas as pd
import numpy as np
import itertools
import argparse
import os


def make_synth_data():
    """
    makes a synthetic data set in a narrow format. synthetic data is plate reader data.

    for configuration:
    observed_output_col = 'observed_fluor'
    intended_output_col = 'intended_output'
    intended_output_col_on = '1'
    intended_output_col_off = '0'

    'exp_str': ['experiment_id', 'strain'],
    'exp_str_ts': ['experiment_id', 'strain', 'output_id'],
    'exp_str_ts_rep': ['experiment_id', 'strain', 'output_id', 'replicate']

    :return: pandas.DataFrame, columns: ['experiment_id', 'output_id', 'time', 'replicate', 'intended_output',
       'input', 'observed_fluor']

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
        if record['intended_output'] == '0':
            mu, sigma = 100, 25
        else:
            mu, sigma = 1000, 250
        observed_fluor = np.random.normal(mu, sigma, 1)[0]
        record.update({'observed_fluor': observed_fluor})

    data_df = pd.DataFrame(records)

    return data_df


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("output_path", help="output_path")
    args = parser.parse_args()
    output_path = args.output_path
    
    dta = make_synth_data()
    
    output_path = os.path.join(output_path, "synthetic_data.csv")
    
    dta.to_csv(output_path, index=False)
