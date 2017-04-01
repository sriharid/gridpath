#!/usr/bin/env python
# Copyright 2017 Blue Marble Analytics LLC. All rights reserved.

"""
Add project-level components for upward frequency response reserves that also 
depend on operational type
"""
import csv
import os.path

from gridpath.project.operations.reserves.op_type_dependent.\
    reserve_limits_by_op_type import \
    generic_add_model_components, generic_load_model_data


# Inputs
RESERVE_PROVISION_RAMP_RATE_LIMIT_COLUMN_NAME_IN_INPUT_FILE = \
    "frequency_response_ramp_rate_limit"
# Model components
RESERVE_PROVISION_VARIABLE_NAME = "Provide_Frequency_Response_MW"
RESERVE_PROVISION_RAMP_RATE_LIMIT_CONSTRAINT_NAME = \
    "Frequency_Response_Provision_Ramp_Rate_Limit_Constraint"
RESERVE_PROVISION_RAMP_RATE_LIMIT_PARAM_NAME = \
    "frequency_response_ramp_rate_limit"
RESERVE_PROJECTS_SET_NAME = "FREQUENCY_RESPONSE_PROJECTS"
RESERVE_PROJECT_OPERATIONAL_TIMEPOINTS_SET_NAME = \
    "FREQUENCY_RESPONSE_PROJECT_OPERATIONAL_TIMEPOINTS"


def add_model_components(m, d):
    """

    :param m:
    :param d:
    :return:
    """

    generic_add_model_components(
        m=m,
        d=d,
        reserve_projects_set=RESERVE_PROJECTS_SET_NAME,
        reserve_project_operational_timepoints_set=
        RESERVE_PROJECT_OPERATIONAL_TIMEPOINTS_SET_NAME,
        reserve_provision_variable_name=RESERVE_PROVISION_VARIABLE_NAME,
        reserve_provision_ramp_rate_limit_param
        =RESERVE_PROVISION_RAMP_RATE_LIMIT_PARAM_NAME,
        reserve_provision_ramp_rate_limit_constraint=
        RESERVE_PROVISION_RAMP_RATE_LIMIT_CONSTRAINT_NAME,
    )


def load_model_data(m, d, data_portal, scenario_directory, horizon, stage):
    """

    :param m:
    :param d:
    :param data_portal:
    :param scenario_directory:
    :param horizon:
    :param stage:
    :return:
    """
    generic_load_model_data(
        m=m,
        d=d,
        data_portal=data_portal,
        scenario_directory=scenario_directory,
        horizon=horizon,
        stage=stage,
        ramp_rate_limit_column_name
        =RESERVE_PROVISION_RAMP_RATE_LIMIT_COLUMN_NAME_IN_INPUT_FILE,
        reserve_provision_ramp_rate_limit_param
        =RESERVE_PROVISION_RAMP_RATE_LIMIT_PARAM_NAME
    )


def get_inputs_from_database(subscenarios, c, inputs_directory):
    """

    :param subscenarios
    :param c:
    :param inputs_directory:
    :return:
    """

    # Get frequency_response ramp rate limit
    prj_ramp_rates = c.execute(
        """SELECT project, frequency_response_ramp_rate
        FROM inputs_project_operational_chars
        WHERE project_operational_chars_scenario_id = {};""".format(
            subscenarios.PROJECT_OPERATIONAL_CHARS_SCENARIO_ID
        )
    ).fetchall()
    # Make a dict for easy access
    prj_ramp_rate_dict = dict()
    for (prj, ramp_rate) in prj_ramp_rates:
        prj_ramp_rate_dict[str(prj)] = \
            "." if ramp_rate is None else str(ramp_rate)

    # Add params to projects file
    with open(os.path.join(inputs_directory, "projects.tab"), "r"
              ) as projects_file_in:
        reader = csv.reader(projects_file_in, delimiter="\t")

        new_rows = list()

        # Append column header
        header = reader.next()
        header.append("frequency_response_ramp_rate")
        new_rows.append(header)

        # Append correct values
        for row in reader:
            # If project specified, check if ramp rate specified or not
            if row[0] in prj_ramp_rate_dict.keys():
                row.append(prj_ramp_rate_dict[row[0]])
            # If project not specified, specify no ramp rate
            else:
                row.append(".")

            # Add resulting row to new_rows list
            new_rows.append(row)

    with open(os.path.join(inputs_directory, "projects.tab"), "w") as \
            projects_file_out:
        writer = csv.writer(projects_file_out, delimiter="\t")
        writer.writerows(new_rows)
