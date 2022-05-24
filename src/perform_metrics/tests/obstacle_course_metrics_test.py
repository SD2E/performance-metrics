"""
Tests for the obstacle_course_metrics.py script

:author: Tessa Johnson
:email: tessa<dot>johnson<at>geomdata<dot>com
:created: 2020 06 05
:copyright: (c) 2020, GDA
:license: All Rights Reserved, see LICENSE for more details
"""

import pytest
from perform_metrics.aggregate_metrics import *
from perform_metrics.group_metrics import metrics_info


class TestObstacleCourse(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        """
        setup for tests
        """
        self.data = pd.read_csv('./src/perform_metrics/example/synthetic_data.csv', dtype=object)

    def test_compute_metric(self):
        """
        Tests for the `compute_metric()` function:
            1. Check the correct number of records is returned
            2. Check the on_count/off_count values are correct
            3. Check the column names are being properly created
        """

        records_df = compute_metrics(self.data, ["experiment_id", "strain"], "observed_fluor",
                                     {"col": "intended_output", "off": "0", "on": "1"}, metrics_info[0]['function'])

        # Check the correct number of records is returned
        # i.e. the number of groups * 3 percentile values
        assert len(records_df) == (len(np.unique(self.data['experiment_id']))*len(np.unique(self.data['strain']))*3)

        # check the on_count/off_count values are correct - we just have to check that all the values are 15 for this
        # because of how the synthetic_data.csv is constructed - see make_synth_data.py
        assert np.unique(records_df['off_count']) == 15
        assert np.unique(records_df['on_count']) == 15

        # check the column names are being properly created
        assert list(records_df.columns) == ['experiment_id', 'strain', 'group_name', 'off_count', 'on_count',
                                            'percentile', 'off_agg', 'on_agg', 'diff', 'ratio']
