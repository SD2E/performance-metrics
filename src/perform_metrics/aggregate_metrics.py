"""
metrics of ON vs OFF for plate reader or aggregated flow cytometry data (one measurement per sample).

:author: Anastasia Deckard (anastasia.deckard@geomdata.com), Tessa Johnson (tessa.johnson@gmail.com)
:copyright: (c) 2020, Geometric Data Analytics, Inc.
:license: see LICENSE for more details
"""

import argparse
import json
import os
import platform
import shutil
from collections import OrderedDict
from datetime import datetime

import matplotlib
import numpy as np
import pandas as pd

if platform.system() == "Darwin":
    matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns

from perform_metrics.group_metrics import metrics_info
from perform_metrics.config_parsing import parse_intended_output


def compute_metrics(data_df, group_cols, observed_output, intended_output, function):
    """
    function to compute all the different intervals for analyzing fold change

    :param function: list of functions to compute metrics with
    :param intended_output: dictionary of values associated with the intended output of the on/off states
    :param observed_output: column name associated with the observed output
    :param data_df: pandas.DataFrame of the data
    :param group_cols: list of columns to group by
    :return: pandas.DataFrame
    """

    # group by the exp and ts ids
    records = list()
    grouped_df = data_df.groupby(group_cols)
    for name, group in grouped_df:
        # compute max of OFF and min of ON
        off = group[(group[intended_output['col']] == intended_output['off'])][
            observed_output].astype(
            'float')
        on = group[(group[intended_output['col']] == intended_output['on'])][
            observed_output].astype(
            'float')  # .to_list()
        # TODO: just use len of above? was planning to do other metrics, but just think count is okay
        off_count = off.count()
        on_count = on.count()

        # identifier part of record
        name_list = [name] if isinstance(name, str) else name
        record = OrderedDict(zip(group_cols, name_list))
        record['group_name'] = name
        record['off_count'] = off_count
        record['on_count'] = on_count

        # metric part of records
        metric_records = function(on, off)

        # merge identifier records and metric records
        # makes a new dict (from entries, not ref to shared record) and *hopefully* preserve the order.
        rec_merge = [OrderedDict(**record, **met_rec) for met_rec in metric_records]
        records.extend(rec_merge)

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
        # out_file.write(doc_info)
        out_file.write(comments)
        out_file.write("# \n")
        results_df.to_csv(out_file, sep='\t', header=True, index=False)


def run_functions(data_df, config_json, output_dir):
    """
    measure fold and absolute change between percentiles and/or mean +/- standard deviation,
    for each experiment, strain - this combines all time series, replicates, and time points

    :param output_dir: directory to save output to
    :param config_json: configuration file
    :param data_df: pandas.DataFrame with the data in it
    :return:
            full_results_df_dict: dictionary with all the results from the analysis
            files: list of file names which contain the output
    """

    observed_output = config_json['observed_output']
    intended_output = config_json['intended_output']
    group_cols_dict = config_json['group_cols_dict']

    files = []
    full_results_df_dict = []
    for metric_dict in metrics_info:
        results_df_dict = dict()
        for key, group_cols in group_cols_dict.items():
            results_df = compute_metrics(data_df=data_df,
                                         group_cols=group_cols,
                                         observed_output=observed_output,
                                         intended_output=intended_output, function=metric_dict['function'])
            results_df_dict[key] = results_df
            comment = metric_dict['comments'] + "{0:s}".format(', '.join(group_cols))
            file_name = metric_dict['file_name'] + "_{0:s}.tsv".format(key)
            out_path = os.path.join(output_dir, file_name)
            save_df(results_df, comment, out_path)
            files.append(file_name)
        full_results_df_dict.append({'metric': metric_dict['metric'], 'record_df_dict': results_df_dict,
                                     "plot_metric": metric_dict["plot_metric"]})

    return full_results_df_dict, files


def plot_on_vs_off(data_df, config_json, file_name, output_dir):
    """
    for each group_cols combination listed in the config, stacked boxplots comparing the distribution
    of on values vs. the distribution of off values is displayed

    :param data_df: dataframe containing the data
    :param config_json: configuration file
    :param file_name: experiment reference (or data file name) to put in the title of the plot
    :param output_dir: directory to save output to
    """

    observed_output = config_json['observed_output']
    intended_output = config_json['intended_output']
    group_cols_dict = config_json['group_cols_dict']

    out_col = intended_output['col']
    out_on = intended_output['on']
    out_off = intended_output['off']
    out_str = '{0:s} on: {1}, off: {2}'.format(out_col, out_on, out_off)

    for key, group_cols in group_cols_dict.items():
        grp = '_'.join(group_cols)
        grouped_df = data_df.groupby(group_cols)
        df = []
        ratio = []
        nm_for_order = []
        for name, group in grouped_df:
            off = group[(group[intended_output['col']] == intended_output['off'])][observed_output]
            on = group[(group[intended_output['col']] == intended_output['on'])][observed_output]
            if len(off) > 0 and len(on) > 0:
                ratio.append(on.median() / (off.median() + 1.0e-20))
                n = ', '.join(name) if isinstance(name, (list, tuple)) else name
                nm_for_order.append(n)
                for i in off:
                    df.append([n, 'off', i])
                for j in on:
                    df.append([n, 'on', j])
        tmp_arr = np.array(ratio)
        order = np.argsort(-tmp_arr)

        data = pd.DataFrame(df, columns=[grp, intended_output['col'], observed_output])

        grp_order = [nm_for_order[i] for i in order]

        data = data.astype({observed_output: float})
        if len(data) > 0:
            fig_height = 3 + 0.1 * grouped_df.ngroups
            plt.figure(figsize=(12, fig_height))
            sns_plot = sns.boxplot(x=observed_output, y=grp,
                                   hue=intended_output['col'], order=grp_order,
                                   data=data)
            sns_plot.set_title("On Vs. Off Boxplot \n {} \n groupby: {} \n {}".format(file_name, key, out_str))
            plt.tight_layout()
            img_name = "on_vs_off_" + key
            out_path = os.path.join(output_dir, img_name)
            fig = sns_plot.get_figure()
            fig.savefig(out_path)
            plt.close()


def plot_histogram_of_fold_changes(results_df_dict, config_json, file_name, output_dir):
    """
    For each group_cols combination listed in the config, a histogram is produced tabulating
    the number of groups that have certain ratios of on/off

    :param results_df_dict: dictionary with all the results from the analysis
    :param config_json: configuration file
    :param file_name: experiment reference (or data file name) to put in the title of the plot
    :param output_dir: directory to save output to
    """

    intended_output = config_json['intended_output']
    out_col = intended_output['col']
    out_on = intended_output['on']
    out_off = intended_output['off']
    out_str = '{0:s} on: {1}, off: {2}'.format(out_col, out_on, out_off)

    for metric_dict in results_df_dict:
        results_dict = metric_dict['record_df_dict']
        metric, metric_val = metric_dict["plot_metric"]

        for key in results_dict.keys():
            assert metric in results_dict[key].columns, '{} is not a column in this dataframe'
            ratio_val = results_dict[key][results_dict[key][metric] == metric_val]['ratio']
            bins = list(range(0, 15, 1))

            hist = sns.distplot(ratio_val, kde=False, bins=bins,
                                hist_kws={"rwidth": 0.75})
            hist.set_title(
                "Group counts per metric histogram \n {} \n groupby: {} \n {} \n {} = {}".format(file_name, key,
                                                                                                 out_str, metric,
                                                                                                 metric_val))
            hist.set(xlabel='ratio on/off', ylabel='Counts')
            plt.tight_layout()

            fig = hist.get_figure()

            img_name = "fold_change_histogram_" + metric_dict['metric'] + '_' + key
            out_path = os.path.join(output_dir, img_name)

            fig.savefig(out_path)
            plt.close()


def run_analysis(data_df, config_json, output_dir, input_file_name):
    """
    Function to run all the analysis and produce all the plots - this is called by run_analysis.py

    :param data_df: dataframe with the data
    :param config_json: configuration file
    :param output_dir: directory to save output to
    :param input_file_name:  experiment reference (or input data file name) to put in the title of the plots
    :return: files: file names for the output
    """

    print('making tables')
    results_df_dict, files = run_functions(data_df, config_json, output_dir)

    print('making plots')
    plot_on_vs_off(data_df, config_json, input_file_name, output_dir)
    plot_histogram_of_fold_changes(results_df_dict, config_json, input_file_name, output_dir)

    return files


def make_sub_directory(out_dir, input_file_name):
    """
    Function to make a subdirectory to save output to - it has the form
    out_dir/input_file_name_metrics_{DATETIME STAMP}/

    :param out_dir: directory to save output to
    :param input_file_name: experiment reference (or input data file name)
    :return: out_dir: new output directory
    """

    now = datetime.now()
    datetime_stamp = now.strftime('%Y%m%d%H%M%S')
    out_dir = os.path.join(out_dir, input_file_name + "_metrics_" + datetime_stamp)
    print("making directory... ", out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    return out_dir


if __name__ == '__main__':

    # TODO: deprecated? Are we ever going to want to use this not with the per sample metrics?

    # Load the config file from user input file location
    parser = argparse.ArgumentParser()

    parser.add_argument("config_file", help="config file")
    parser.add_argument("data_path", help="input file with data")
    parser.add_argument("output_dir", help="directory for output")
    parser.add_argument("-n", "--no_sub_dir", help="do not make a subdirectory (not recommended except for reactor)",
                        action="store_true")

    args = parser.parse_args()

    config_file_loc = args.config_file
    data_path = args.data_path
    output_dir_loc = args.output_dir
    arg_no_sub_dir = args.no_sub_dir

    input_file_name_loc, input_file_ext = os.path.splitext(os.path.basename(data_path))

    if not arg_no_sub_dir:
        output_dir_loc = make_sub_directory(output_dir_loc, input_file_name_loc)

    shutil.copy(config_file_loc, output_dir_loc)

    print("loading data")
    with open(config_file) as json_file:
        config_json = json.load(json_file)

    data_df_loc = pd.read_csv(data_path, dtype=object)

    config_json_loc = parse_intended_output(config_json_loc, data_df_loc, output_dir_loc, config_file_loc)

    run_analysis(data_df_loc, config_json_loc, output_dir_loc, input_file_name_loc)

    print("finished")
