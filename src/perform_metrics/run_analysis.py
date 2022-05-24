"""
Runner to run the following analysis:
    1. Aggregate metrics (from obstacle_course_metrics.py)
    2. Per sample metrics (from sample_metrics.py)

:author: Tessa Johnson (tessa.johnson@geomdata.com)
:copyright: (c) 2020, Geometric Data Analytics, Inc.
:license: see LICENSE for more details
"""

import argparse
import json
import os
from datetime import datetime
import shutil
import pandas as pd
from perform_metrics.config_parsing import parse_intended_output
from perform_metrics.sample_metrics import run_functions as run_per_sample
from perform_metrics.aggregate_metrics import run_analysis as run_aggregate
import perform_metrics.make_record as rec


def make_sub_directory(out_dir, input_file_name):
    """
    Function to make an optional subdirectory based on the datetime and experiment name

    :param out_dir: output directory
    :param input_file_name: experiment reference (or data file name) for directory name
    :return: out_dir: new output directory name
    """

    now = datetime.now()
    datetime_stamp = now.strftime('%Y%m%d%H%M%S')
    out_dir = os.path.join(out_dir, input_file_name + "_metrics_" + datetime_stamp)
    print("making directory... ", out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    return out_dir


def main(config_file, data_path, output_dir, input_file_name, merge_files):
    """
    Main function to run all of the analysis - both aggregate and per sample. This run will also hash the files and
    make a records json.

    :param config_file: Configuration file
    :param data_path: Path to data
    :param output_dir: Output directory
    :param input_file_name: experimental reference (or data file name)
    :param merge_files: Metadata file to merge with (optional).
    """

    with open(config_file) as json_file:
        config_json = json.load(json_file)

    data_df = pd.read_csv(data_path, dtype=object)

    if merge_files is not None:
        metadata_df = pd.read_csv(merge_files, dtype=object)
        data_df = pd.merge(data_df, metadata_df, on=config_json['sample_id'])

    if "subset_by" in config_json.keys():
        for col, val in config_json["subset_by"].items():
            data_df = data_df[data_df[col] == val]

    config_json = parse_intended_output(config_json, data_df, output_dir, config_file)

    saved_files = list()

    print('running per sample analysis...')
    _, sample_files = run_per_sample(data_df=data_df, config_json=config_json, output_dir=output_dir)
    saved_files.extend(sample_files)

    print('running aggregate analysis...')
    agg_files = run_aggregate(data_df, config_json, output_dir, input_file_name)
    saved_files.extend(agg_files)

    # get files together for summarizing and hashing
    files = [{'name': x} for x in saved_files]

    # make hash for data sets
    print("hashing output...")
    files = rec.make_hashes_for_files(output_dir, files)

    # make data record
    print("making product record...")
    record = rec.make_product_record(output_dir, files,  data_path)

    record_path = os.path.join(output_dir, "record.json")
    with open(record_path, 'w') as json_file:
        json.dump(record, json_file, indent=2)

    print("finished!")


if __name__ == '__main__':

    # Load the config file from user input file location
    parser = argparse.ArgumentParser()

    parser.add_argument("config_file", help="config file")
    parser.add_argument("data_path", help="input file with data")
    parser.add_argument("output_dir", help="directory for output")
    parser.add_argument("-n", "--no_sub_dir", help="do not make a subdirectory (not recommended except for reactor)",
                        action="store_true")
    parser.add_argument('-m', "--merge_files", help='if there is a seperate metadata file, specify its location here')

    args = parser.parse_args()

    config_file_loc = args.config_file
    data_path_loc = args.data_path
    output_dir_loc = args.output_dir
    merge_files_loc = args.merge_files
    arg_no_sub_dir = args.no_sub_dir

    input_file_name_loc, input_file_ext = os.path.splitext(os.path.basename(data_path_loc))

    if not arg_no_sub_dir:
        output_dir_loc = make_sub_directory(output_dir_loc, input_file_name_loc)
    else:
        if not os.path.exists(output_dir_loc):
            os.makedirs(output_dir_loc, exist_ok=True)

    shutil.copy(config_file_loc, output_dir_loc)

    main(config_file_loc, data_path_loc, output_dir_loc, input_file_name_loc, merge_files_loc)
