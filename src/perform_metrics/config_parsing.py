"""
code for parsing the config files

:author: Tessa Johnson (tessa.johnson@geomdata.com)
:copyright: (c) 2020, Geometric Data Analytics, Inc.
:license: , see LICENSE for more details
"""

import numpy as np
import json
import os


def parse_intended_output(config_json, data_df, output_dir, config_file):
    """
    Function to parse the intended output column of the config when a more general value is used, e.g. "max" or "min"

    :param config_json: Config file
    :param data_df: Data set associated with the config file
    :param output_dir: Output directory
    :param config_file: Config file name
    :return: config with the correct values for the intended output
    """
    output_funct = {"max": np.nanmax, "min": np.nanmin}

    if config_json['intended_output']['on'] in output_funct.keys():
        tmp_output_on = {float(x): x for x in data_df[config_json['intended_output']['col']]}
        on_float = output_funct[config_json['intended_output']['on']](list(tmp_output_on.keys()))
        config_json['intended_output']['on'] = tmp_output_on[on_float]

    if config_json['intended_output']['off'] in output_funct.keys():
        tmp_output_off = {float(x): x for x in data_df[config_json['intended_output']['col']]}
        off_float = output_funct[config_json['intended_output']['off']](list(tmp_output_off.keys()))
        config_json['intended_output']['off'] = tmp_output_off[off_float]

    confil_file_name, config_file_ext = os.path.splitext(os.path.basename(config_file))
    out_path = os.path.join(output_dir, confil_file_name + '_evaluated.json')
    with open(out_path, 'w') as outfile:
        json.dump(config_json, outfile, indent=2)

    return config_json
