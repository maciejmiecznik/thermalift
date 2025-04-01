# -*- coding: utf-8 -*-
"""
Thermalift, version 1.0
Last updated on April 1, 2025

author: Maciej Miecznik
affiliation: Mineral and Energy Economy Research Institute,
             Polish Academy of Sciences
             Wybickiego 7A, 31-261 Kraków, Poland
e-mail: miecznik@min-pan.krakow.pl

This code demonstrates the use of Thermalift 1.0 with some input files that
require prior manipulation, data extraction, interpolation, etc.
Finally, you get graphs and output files that show the influence of thermal lift
effect on the observed water table level in a geothermal well during operation.
"""


import sys
import pandas as pd
import thermalift

# adding lib folder to the system path
sys.path.insert(0, "..\..\lib")


# %% Import static temperature profile of the formation
# Stargard GT-7 well
rock_formation_temperature_file = "formation_temperature.csv"
rock_formation = thermalift.Formation(rock_formation_temperature_file)

rock_formation.data = rock_formation.read_formation_data()
rock_formation.profile = rock_formation.temp_interpolation(0, 3000, 30)
rock_formation.formation_temperature_plot(
    rock_formation.data, rock_formation.profile
)


# %% Import pumping data, remove duplicated columns, filter incorrect data
test_well_zenith = pd.read_csv("zenith_measerements.csv", sep=";", decimal=",")

# Removes duplicate columns with measurement date and time
test_well_zenith = test_well_zenith.drop(
    columns=[
        "ST3_SC_GT6_1_TempWej - Czas",
        "ST3_SC_GT7_1_CisnWej - Czas",
        "ST3_SC_GT7_1_TempWej - Czas",
        "ST1_FIT_GT6_1_Wart - Czas",
        "ST2_FIT_GT7_1_Wart - Czas",
    ]
)

# Changing column names to shorter ones
test_well_zenith.rename(
    columns={
        "ST3_SC_GT6_1_CisnWej - Czas": "time",
        "ST3_SC_GT6_1_CisnWej": "gt6_pressure",
        "ST3_SC_GT6_1_TempWej": "gt6_temperature",
        "ST3_SC_GT7_1_CisnWej": "gt7_pressure",
        "ST3_SC_GT7_1_TempWej": "gt7_temperature",
        "ST1_FIT_GT6_1_Wart": "gt6_flow",
        "ST2_FIT_GT7_1_Wart": "gt7_flow",
    },
    inplace=True,
)

# Converting a time column (type: string) to type 'datetime64[ns]
test_well_zenith["time"] = pd.to_datetime(
    test_well_zenith["time"], errors="raise", dayfirst=True
)

# Data filtering: only measurement points before the Zenith probe failure
test_well_zenith = test_well_zenith[
    test_well_zenith["time"] <= "2022-10-05 12:00:00"
]

# Remove incorrect measurement from 2022-02-05 14:00:00
test_well_zenith = test_well_zenith.drop(test_well_zenith.index[9608])


# %% Create Well class object and perform calculations
test_well = thermalift.Well(test_well_zenith)

# Add properties to the object
test_well.salinity = 126

# Calculate mean static temperature in the wellbore
test_well.mean_stat_temp = test_well.temp_static(rock_formation.profile)

# Calculate mean dynamic temperature in the flowing well
test_well.mean_flowing_temp = test_well.temp_flowing(
    rock_formation.profile, 1, test_well_zenith, 4
)

# Calculate mean water column density in a non-flowing well
test_well.mean_stat_dens = test_well.dens_static(
    test_well.mean_stat_temp, test_well.salinity
)

# Calculate mean water column density in flowing well
test_well.mean_flowing_dens = test_well.dens_dynamic(
    test_well.mean_flowing_temp, test_well.salinity
)

# Calculate water level in flowing well
test_well.water_level = test_well.water_level(
    test_well.pumping_input.iloc[:, 3],
    test_well.mean_flowing_dens,
    probe_depth=272.28,
    atmo_pressure=101325,
)

# Calculate measured drawdown
test_well.recorded_drawdown = test_well.measured_drawdown(
    test_well.water_level
)

# Calculate true water level, after eliminating thermal lift
test_well.true_water_level = test_well.true_water_level(
    test_well.water_level,
    test_well.mean_flowing_dens,
    test_well.mean_stat_dens,
    depth_max=2700.0,
)

# Calculate true drawdown, after eliminating thermal lift
test_well.true_drawdown = test_well.true_drawdown(test_well.true_water_level)

# Save results to file
test_well.save_results(filename="results.xlsx")

# %% Figures
test_well.raw_data_plot(
    test_well.pumping_input.iloc[:, 0],
    test_well.pumping_input.iloc[:, 5],
    test_well.pumping_input.iloc[:, 4],
    test_well.pumping_input.iloc[:, 3],
    title="Test well raw data",
)

test_well.mosaic_plot(
    test_well.pumping_input.iloc[:, 0],
    test_well.pumping_input.iloc[:, 6],
    test_well.mean_flowing_temp,
    test_well.mean_flowing_dens,
    test_well.water_level,
    test_well.true_water_level,
    test_well.recorded_drawdown,
    test_well.true_drawdown,
    bounds=False,
    show_fit=True,
    title="Test well raw and corrected pumping data",
    figsize=(25, 12),
)
