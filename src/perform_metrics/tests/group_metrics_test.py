"""
Tests for the analysis_var_part.py script

:author: Tessa Johnson
:email: tessa<dot>johnson<at>geomdata<dot>com
:created: 2020 06 04
:copyright: (c) 2020, GDA
:license: All Rights Reserved, see LICENSE for more details
"""

import pytest
from perform_metrics.group_metrics import *


class TestGroupMetric(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        """
        setup for tests
        """
        self.on = np.arange(100, 201, 1)
        self.off = np.arange(0, 101, 1)

    # Todo: I'm realizing that I don't really know the proper way to format tests (or if there is a proper way),
    #  i.e. I have a single test for each function and a bunch of asserts within that test, but is it better to have
    #  an individual test for each thing I'm testing? Also, I basically ran the same tests on both of these functions
    #  so would it be better to somehow combine the tests? If so, I have no idea hwo to do that

    def test_compute_metric_percentile(self):
        """
        Tests for the `compute_metric_percent()` function:
            1. Checking the correct number of records are returned
            2. Check the order types of objects are being returned
            3. Check the correct OrderDict's are being returned
            4. Checking the correct values are being computed
        """

        records = compute_metric_percent(self.on, self.off)

        # This only records if one of the tests below fails
        print(records)

        # Check it's returning the correct number of values
        assert len(records) == 3, 'This function should returning 3 records, it is ' \
                                  'currently returning {}'.format(len(records))

        # Check that a list containing OrderedDict is being returned
        assert type(records) is list, 'Records should be list, it is currently a {}'.format(type(records))

        # Check each item is an OrderDict
        for item in records:
            assert type(item) is OrderedDict, 'All records should be OrderDict, this item is a {}'.format(type(records))

        # Check that the OrderDict has the correct keys
        # Note: This also checks it has the correct number of values
        for item in records:
            assert list(item.keys()) == ['percentile', 'off_agg', 'on_agg', 'diff', 'ratio'], \
                "This dictionary doesn't have the correct keys - {}".format(item.keys())

        # checking that the function returns the correct calculated values
        off_agg_correct = [100, 75, 50]
        on_agg_correct = [100, 125, 150]
        diff_correct = [0, 50, 100]
        ratio_correct = [1.0, 125 / 75, 3]

        for i, item in enumerate(records):
            assert item['off_agg'] == off_agg_correct[i], "The correct off_agg value is {}, the function is " \
                                                          "returning {}".format(off_agg_correct[i], item['off_agg'])
            assert item['on_agg'] == on_agg_correct[i], "The correct on_agg value is {}, the function is " \
                                                        "returning {}".format(on_agg_correct[i], item['on_agg'])
            assert item['diff'] == diff_correct[i], "The correct diff value is {}, the function is " \
                                                    "returning {}".format(diff_correct[i], item['diff'])
            assert item['ratio'] == ratio_correct[i], "The correct ratio value is {}, the function is " \
                                                      "returning {}".format(ratio_correct[i], item['ratio_agg'])

        # check we get the correct behavior if there is an NAN value in the data - it should return the same values
        # as above
        on_w_na = np.r_[self.on, np.nan]
        off_w_na = np.r_[self.off, np.nan]

        records_w_na = compute_metric_percent(on_w_na, off_w_na)

        assert records_w_na == records, 'Your function appears to not be ignoring NA values'

    def test_compute_metric_sd(self):
        """
        Tests for the `compute_metric_sd()` function:
            1. Checking the correct number of records are returned
            2. Check the order types of objects are being returned
            3. Check the correct OrderDict's are being returned
            4. Checking the correct values are being computed
        """

        records = compute_metric_sd(self.on, self.off)

        # This only records if one of the tests below fails
        print(records)

        # Check it's returning the correct number of values
        assert len(records) == 4, 'This function should returning 4 records, it is ' \
                                  'currently returning {}'.format(len(records))

        # Check that a list containing OrderedDict is being returned
        assert type(records) is list, 'Records should be list, it is currently a {}'.format(type(records))

        # Check each item is an OrderDict
        for item in records:
            assert type(item) is OrderedDict, 'All records should be OrderDict, this item is a {}'.format(type(records))

        # Check that the OrderDict has the correct keys
        # Note: This also checks it has the correct number of values
        for item in records:
            assert list(item.keys()) == ['num_std', 'off_agg', 'on_agg', 'diff', 'ratio'], "This dictionary doesn't" \
                                                                                              "have the correct keys " \
                                                                                              "- {}".format(item.keys())
        # checking that the function returns the correct calculated values
        off_agg_correct = [50, 50+np.std(self.off), 50+2*np.std(self.off), 50+3*np.std(self.off)]
        on_agg_correct = [150, 150-np.std(self.on), 150-2*np.std(self.on), 150-3*np.std(self.on)]
        diff_correct = [100, on_agg_correct[1]-off_agg_correct[1], on_agg_correct[2]-off_agg_correct[2],
                        on_agg_correct[3]-off_agg_correct[3]]
        ratio_correct = [3, on_agg_correct[1]/off_agg_correct[1], on_agg_correct[2]/off_agg_correct[2],
                         on_agg_correct[3]/off_agg_correct[3]]

        for i, item in enumerate(records):
            assert item['off_agg'] == off_agg_correct[i], "The correct off_agg value is {}, the function is " \
                                                          "returning {}".format(off_agg_correct[i], item['off_agg'])
            assert item['on_agg'] == on_agg_correct[i], "The correct on_agg value is {}, the function is " \
                                                        "returning {}".format(on_agg_correct[i], item['on_agg'])
            assert item['diff'] == diff_correct[i], "The correct diff value is {}, the function is " \
                                                    "returning {}".format(diff_correct[i], item['diff'])
            assert item['ratio'] == ratio_correct[i], "The correct ratio value is {}, the function is " \
                                                      "returning {}".format(ratio_correct[i], item['ratio_agg'])

        on_w_na = np.r_[self.on, np.nan]
        off_w_na = np.r_[self.off, np.nan]

        records_w_na = compute_metric_sd(on_w_na, off_w_na)

        assert records_w_na == records, 'Your function appears to not be ignoring NA values'
