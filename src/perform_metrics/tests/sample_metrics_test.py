"""
Tests for the sample_metrics.py script

:author: Tessa Johnson
:email: tessa<dot>johnson<at>geomdata<dot>com
:created: 2020 08 03
:copyright: (c) 2020, GDA
:license: All Rights Reserved, see LICENSE for more details
"""

import numpy as np
import pytest
from perform_metrics.sample_metrics import *
from perform_metrics.group_metrics import compute_metric_percent


class TestSampleMetric(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        """
        setup for tests
        """
        self.data = pd.read_csv('./src/perform_metrics/example/synthetic_data.csv', dtype=object)

    def test_compute_metric(self):
        """
        Tests for the `compute_metrics()` function:
            1. Check the correct number of records is returned
            2. Check the on_count/off_count values are correct
            3. Check the column names are being properly created
        """

        records_df = compute_metrics(self.data, ["experiment_id", "strain"], "observed_fluor",
                                     {"col": "intended_output", "off": "0", "on": "1"}, compute_metric_percent,
                                     sample_id="sample_id")

        # Check the correct number of records is returned
        assert len(records_df) == self.data.shape[0]

        # check there is the correct number of sample ids
        assert len(np.unique(records_df['sample_id'])) == self.data.shape[0]

        # check the on_count/off_count values are correct - we just have to check that all the values are 15 for this
        # because of how the synthetic_data.csv is constructed - see make_synth_data.py or 1 if they are for a single
        # sample
        assert np.array_equal(np.unique(records_df['off_count']), [1, 15])
        assert np.array_equal(np.unique(records_df['on_count']), [1, 15])

        # check the column names are being properly created
        assert list(records_df.columns) == ['experiment_id', 'strain', 'group_name', 'off_count', 'on_count',
                                            'sample_id', 'percentile', 'off_agg', 'on_agg', 'diff', 'ratio']

        # check one on and one off value

        # get first on value
        on_vals = records_df[records_df['on_count'] == 1].iloc[0, :]

        # check ratio and diff
        assert (on_vals['on_agg']-on_vals['off_agg']) == on_vals['diff']
        assert (on_vals['on_agg']/on_vals['off_agg']) == on_vals['ratio']

        # get first off value
        off_vals = records_df[records_df['off_count'] == 1].iloc[0, :]

        # check ratio and diff
        assert (off_vals['on_agg'] - off_vals['off_agg']) == off_vals['diff']
        assert (off_vals['on_agg'] / off_vals['off_agg']) == off_vals['ratio']

