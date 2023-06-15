# Copyright 2016-2020 Blue Marble Analytics LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from collections import OrderedDict
from importlib import import_module
import os.path
import pandas as pd
import sys
import unittest

from tests.common_functions import create_abstract_model, add_components_and_load_data

TEST_DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), "..", "..", "test_data")

# Import prerequisite modules
PREREQUISITE_MODULE_NAMES = [
    "temporal.operations.timepoints",
    "temporal.operations.horizons",
    "temporal.investment.periods",
    "geography.load_zones",
    "project",
    "project.capacity.capacity",
]
NAME_OF_MODULE_BEING_TESTED = "project.capacity.relative_capacity"
IMPORTED_PREREQ_MODULES = list()
for mdl in PREREQUISITE_MODULE_NAMES:
    try:
        imported_module = import_module("." + str(mdl), package="gridpath")
        IMPORTED_PREREQ_MODULES.append(imported_module)
    except ImportError:
        print("ERROR! Module " + str(mdl) + " not found.")
        sys.exit(1)
# Import the module we'll test
try:
    MODULE_BEING_TESTED = import_module(
        "." + NAME_OF_MODULE_BEING_TESTED, package="gridpath"
    )
except ImportError:
    print("ERROR! Couldn't import module " + NAME_OF_MODULE_BEING_TESTED + " to test.")


class TestRelativeCapacity(unittest.TestCase):
    """ """

    def test_add_model_components(self):
        """
        Test that there are no errors when adding model components
        :return:
        """
        create_abstract_model(
            prereq_modules=IMPORTED_PREREQ_MODULES,
            module_to_test=MODULE_BEING_TESTED,
            test_data_dir=TEST_DATA_DIRECTORY,
            subproblem="",
            stage="",
        )

    def test_load_model_data(self):
        """
        Test that data are loaded with no errors
        :return:
        """
        add_components_and_load_data(
            prereq_modules=IMPORTED_PREREQ_MODULES,
            module_to_test=MODULE_BEING_TESTED,
            test_data_dir=TEST_DATA_DIRECTORY,
            subproblem="",
            stage="",
        )

    def test_initialized_components(self):
        """
        Create components; check they are initialized with data as expected.
        Capacity-type modules should have added appropriate data;
        make sure it is all as expected.
        """
        m, data = add_components_and_load_data(
            prereq_modules=IMPORTED_PREREQ_MODULES,
            module_to_test=MODULE_BEING_TESTED,
            test_data_dir=TEST_DATA_DIRECTORY,
            subproblem="",
            stage="",
        )
        instance = m.create_instance(data)

        # Set: RELATIVE_CAPACITY_PROJECT_PAIR_PERIODS
        expected_prj_prd = sorted(
            [("Battery", "Wind", 2020), ("Battery", "Wind", 2030)]
        )
        actual_prj_prd = sorted(
            [
                (prj, prj_l, period)
                for (
                    prj,
                    prj_l,
                    period,
                ) in instance.RELATIVE_CAPACITY_PROJECT_PAIR_PERIODS
            ]
        )
        self.assertListEqual(expected_prj_prd, actual_prj_prd)

        # Params: min_relative_capacity_limit_new
        expected_new_min = {
            ("Battery", "Wind", 2020): 0,
            ("Battery", "Wind", 2030): 1,
        }
        actual_new_min = {
            (prj, prj_for_lim, prd): instance.min_relative_capacity_limit_new[
                prj, prj_for_lim, prd
            ]
            for (
                prj,
                prj_for_lim,
                prd,
            ) in instance.RELATIVE_CAPACITY_PROJECT_PAIR_PERIODS
        }
        self.assertDictEqual(expected_new_min, actual_new_min)

        # # Params: max_relative_capacity_limit_new
        expected_new_max = {
            ("Battery", "Wind", 2020): 2,
            ("Battery", "Wind", 2030): float("inf"),
        }
        actual_new_max = {
            (prj, prj_for_lim, prd): instance.max_relative_capacity_limit_new[
                prj, prj_for_lim, prd
            ]
            for (
                prj,
                prj_for_lim,
                prd,
            ) in instance.RELATIVE_CAPACITY_PROJECT_PAIR_PERIODS
        }
        self.assertDictEqual(expected_new_max, actual_new_max)

        # Params: min_relative_capacity_limit_total
        expected_total_min = {
            ("Battery", "Wind", 2020): 3,
            ("Battery", "Wind", 2030): 0,
        }
        actual_total_min = {
            (prj, prj_for_lim, prd): instance.min_relative_capacity_limit_total[
                prj, prj_for_lim, prd
            ]
            for (
                prj,
                prj_for_lim,
                prd,
            ) in instance.RELATIVE_CAPACITY_PROJECT_PAIR_PERIODS
        }
        self.assertDictEqual(expected_total_min, actual_total_min)

        # Params: max_relative_capacity_limit_total
        expected_total_max = {
            ("Battery", "Wind", 2020): float("inf"),
            ("Battery", "Wind", 2030): 4,
        }
        actual_total_max = {
            (prj, prj_for_lim, prd): instance.max_relative_capacity_limit_total[
                prj, prj_for_lim, prd
            ]
            for (
                prj,
                prj_for_lim,
                prd,
            ) in instance.RELATIVE_CAPACITY_PROJECT_PAIR_PERIODS
        }
        self.assertDictEqual(expected_total_max, actual_total_max)
