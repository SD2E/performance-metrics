"""
Functions to compute a circuit performance metric on a per sample basis

:author: Tessa Johnson (tessa.johnson@geomdata.com)
:copyright: (c) 2020, Geometric Data Analytics, Inc.
:license: see LICENSE for more details
"""

import argparse
import json
import os
import pandas as pd
from datetime import datetime
import shutil
from collections import OrderedDict

from perform_metrics.group_metrics import compute_metric_percent
from perform_metrics.config_parsing import parse_intended_output


def compute_metrics(data_df, group_cols, observed_output, intended_output, function, sample_id):
    """
    function to compute all the different intervals for analyzing fold change

    :param function: list of functions to compute metrics with
    :param intended_output: dictionary of values associated with the intended output of the on/off states
    :param observed_output: column name associated with the observed output
    :param data_df: pandas.DataFrame
    :param group_cols: list of columns to group by
    :param sample_id: sample id
    :return: pandas.DataFrame
    """

    # group by the exp and ts ids
    records = list()
    grouped_df = data_df.groupby(group_cols)
    for name, group in grouped_df:
        # compute max of OFF and min of ON
        off = group[(group[intended_output['col']] == intended_output['off'])][observed_output].astype(
            'float')
        on = group[(group[intended_output['col']] == intended_output['on'])][observed_output].astype(
            'float')

        on_ids = group[(group[intended_output['col']] == intended_output['on'])][sample_id]
        off_ids = group[(group[intended_output['col']] == intended_output['off'])][sample_id]

        # identifier part of record
        name_list = [name] if isinstance(name, str) else name

        # get metric for on samples
        for samp_on, on_id in zip(on, on_ids):
            record = OrderedDict(zip(group_cols, name_list))
            record['group_name'] = name
            record['off_count'] = len(off)
            record['on_count'] = 1
            record['sample_id'] = on_id
            metric_records = function([samp_on], off)[2]
            rec_merge = OrderedDict(**record, **metric_records)
            records.append(rec_merge)

        for samp_off, off_id in zip(off, off_ids):
            record = OrderedDict(zip(group_cols, name_list))
            record['group_name'] = name
            record['on_count'] = len(on)
            record['off_count'] = 1
            record['sample_id'] = off_id
            metric_records = function(on, [samp_off])[2]
            rec_merge = OrderedDict(record, **metric_records)
            records.append(rec_merge)

    records_df = pd.DataFrame(records)
    records_df.sort_values(by=group_cols,
                           inplace=True)
    return records_df


def save_df(results_df, comments, out_path):
    """
   Function to save the results dataframe to file

   :param results_df: results dataframe
   :param comments: any comments the user wishes to be added to the output file
   :param out_path: path to save output to
   """

    print("saving to: " + out_path)
    with open(out_path, 'w') as out_file:
        out_file.write(comments)
        out_file.write("# \n")
        results_df.to_csv(out_file, sep='\t', header=True, index=False)


def run_functions(data_df, config_json, output_dir):
    """
    measure fold and absolute change between
    percentiles,
    for each experiment, strain; combine all time series, replicates, and time points
    so group by experiment, strain

    :param output_dir: directory to save output to
    :param config_json: configuration file
    :param data_df: pandas.DataFrame
    :return: pandas.DataFrame
    """

    observed_output = config_json['observed_output']
    intended_output = config_json['intended_output']
    group_cols_dict = config_json['group_cols_dict']
    sample_id = config_json['sample_id']

    files = []
    full_results_df_dict = []
    results_df_dict = dict()
    for key, group_cols in group_cols_dict.items():
        results_df = compute_metrics(data_df=data_df,
                                     group_cols=group_cols,
                                     observed_output=observed_output,
                                     intended_output=intended_output, function=compute_metric_percent,
                                     sample_id=sample_id)
        results_df_dict[key] = results_df
        comment = "# metrics on a per sample basis grouped by:" + "{0:s}".format(', '.join(group_cols))
        file_name = "per_sample_metric" + "_{0:s}.tsv".format(key)
        out_path = os.path.join(output_dir, file_name)
        save_df(results_df, comment, out_path)
        files.append(file_name)

    return full_results_df_dict, files


if __name__ == '__main__':

    # ToDo: Deprecated? Are we only going to want to call this from within run_analysis?

    # Load the config file from user input file location
    parser = argparse.ArgumentParser()

    parser.add_argument("config_file", help="config file")
    parser.add_argument("data_path", help="input file with data")
    parser.add_argument("output_dir", help="directory for output")

    args = parser.parse_args()

    config_file = args.config_file
    data_path = args.data_path
    output_dir_loc = args.output_dir

    print("loading data")
    with open(config_file) as json_file:
        config_json = json.load(json_file)

    now = datetime.now()
    datetime_stamp = now.strftime('%Y%m%d%H%M%S')
    input_file_name, input_file_ext = os.path.splitext(os.path.basename(data_path))
    output_dir_loc = os.path.join(output_dir_loc, input_file_name + "_per_sample_metrics_" + datetime_stamp)

    if not os.path.exists(output_dir_loc):
        os.makedirs(output_dir_loc, exist_ok=True)
    shutil.copy(config_file, output_dir_loc)

    data_df_loc = pd.read_csv(data_path, dtype=object)

    config_json_loc = parse_intended_output(config_json_loc, data_df_loc, output_dir_loc, config_file)

    results_df_dict_loc, files_loc = run_functions(data_df=data_df_loc, config_json=config_json_loc, output_dir=output_dir_loc)
