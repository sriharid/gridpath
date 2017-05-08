#!/usr/bin/env python
# Copyright 2017 Blue Marble Analytics LLC. All rights reserved.

"""
Aggregate carbon emissions from the transmission-line-timepoint level to
the carbon cap zone - period level.
"""

import csv
import os.path
from pyomo.environ import Param, Set, Var, Constraint, Expression, \
    NonNegativeReals, value

from gridpath.auxiliary.dynamic_components import \
    carbon_cap_balance_emission_components


def add_model_components(m, d):
    """
    Aggregate total imports of emissions and add to carbon balance constraint
    :param m:
    :param d:
    :return:
    """
    def total_carbon_emissions_imports_rule(mod, z, p):
        """
        Calculate total emissions from all carbonaceous transmission lines
        imported into the carbon cap zone
        :param mod:
        :param z:
        :param p:
        :return:
        """
        return sum(mod.Import_Carbon_Emissions_Tons[tx, tmp]
                   * mod.number_of_hours_in_timepoint[tmp]
                   * mod.horizon_weight[mod.horizon[tmp]]
                   for (tx, tmp) in
                   mod.CARBONACEOUS_TRANSMISSION_OPERATIONAL_TIMEPOINTS
                   if tx in
                   mod.CARBONACEOUS_TRANSMISSION_LINES_BY_CARBON_CAP_ZONE[z]
                   and tmp in mod.TIMEPOINTS_IN_PERIOD[p]
                   )

    m.Total_Carbon_Emission_Imports_Tons = Expression(
        m.CARBON_CAP_ZONE_PERIODS_WITH_CARBON_CAP,
        rule=total_carbon_emissions_imports_rule
    )

    # Add to emission imports to carbon balance
    getattr(d, carbon_cap_balance_emission_components).append(
        "Total_Carbon_Emission_Imports_Tons"
    )


def export_results(scenario_directory, horizon, stage, m, d):
    """

    :param scenario_directory:
    :param horizon:
    :param stage:
    :param m:
    :param d:
    :return:
    """
    with open(os.path.join(scenario_directory, horizon, stage, "results",
                           "carbon_cap_total_transmission.csv"), "wb") as \
            rps_results_file:
        writer = csv.writer(rps_results_file)
        writer.writerow(["carbon_cap_zone", "period", "carbon_cap_target_mmt",
                         "transmission_carbon_emissions_mmt"])
        for (z, p) in m.CARBON_CAP_ZONE_PERIODS_WITH_CARBON_CAP:
            writer.writerow([
                z,
                p,
                float(m.carbon_cap_target_mmt[z, p]),
                value(
                    m.Total_Carbon_Emission_Imports_Tons[z, p]
                ) / 10**6  # MMT
            ])


def import_results_into_database(
        scenario_id, c, db, results_directory
):
    """

    :param scenario_id:
    :param c:
    :param db:
    :param results_directory:
    :return:
    """
    print("system carbon emissions (imports)")
    # Carbon emissions from imports
    # Prior results should have already been cleared by
    # system.policy.carbon_cap.aggregate_project_carbon_emissions,
    # then project total emissions imported
    # Update results_system_carbon_emissions with NULL just in case (instead of
    # clearing prior results)
    c.execute(
        """UPDATE results_system_carbon_emissions
        SET import_emissions_mmt = NULL
        WHERE scenario_id = {}""".format(
            scenario_id
        )
    )
    db.commit()

    with open(os.path.join(results_directory,
                           "carbon_cap_total_transmission.csv"), "r") as \
            emissions_file:
        reader = csv.reader(emissions_file)

        reader.next()  # skip header
        for row in reader:
            carbon_cap_zone = row[0]
            period = row[1]
            tx_carbon_emissions_mmt = row[3]

            c.execute(
                """UPDATE results_system_carbon_emissions
                SET import_emissions_mmt = {}
                WHERE scenario_id = {}
                AND carbon_cap_zone = '{}'
                AND period = {}""".format(
                    tx_carbon_emissions_mmt, scenario_id, carbon_cap_zone, period
                )
            )
    db.commit()
