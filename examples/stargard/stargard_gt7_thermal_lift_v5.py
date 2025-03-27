# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 11:56:13 2024

@author: miecznik
"""


import sys
import pandas as pd
import thermalift

# adding lib folder to the system path
sys.path.insert(0, "..\..\lib")


# %% Import static temperature profile of the formation
# Stargard GT-7 well
formation_temperature_file = "formation_temperature.csv"
gt7_formation = thermalift.Formation(formation_temperature_file)

gt7_formation.data = gt7_formation.read_formation_data()
gt7_formation.profile = gt7_formation.temp_interpolation(0, 3000, 30)
gt7_formation.formation_temperature_plot(
    gt7_formation.data, gt7_formation.profile
)

"""
# %% Import pumping data, remove duplicated columns, filter incorrect data
gt7_zenith = pd.read_csv("zenith_measerements.csv", sep=";", decimal=",")

# Removes duplicate columns with measurement date and time
gt7_zenith = gt7_zenith.drop(
    columns=[
        "ST3_SC_GT6_1_TempWej - Czas",
        "ST3_SC_GT7_1_CisnWej - Czas",
        "ST3_SC_GT7_1_TempWej - Czas",
        "ST1_FIT_GT6_1_Wart - Czas",
        "ST2_FIT_GT7_1_Wart - Czas",
    ]
)

# Changing column names to shorter ones
gt7_zenith.rename(
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
gt7_zenith["time"] = pd.to_datetime(
    gt7_zenith["time"], errors="raise", dayfirst=True
)

# Data filtering: only measurement points before the gt7_zenith probe failure
gt7_zenith = gt7_zenith[gt7_zenith["time"] <= "2022-10-05 12:00:00"]

# Remove incorrect measurement from 2022-02-05 14:00:00
gt7_zenith = gt7_zenith.drop(gt7_zenith.index[9608])


# %% Create Well class object and perform calculations
stargard_gt7 = thermalift.Well(gt7_zenith)

# Add properties to the object
stargard_gt7.salinity = 126

# Calculate mean static temperature in the wellbore
stargard_gt7.mean_stat_temp = stargard_gt7.temp_static(gt7_formation.profile)

# stargard_gt7.mean_stat_temp = gt7_form_temperature.profile.iloc[:, 0].mean()

# Calculate mean dynamic temperature in the flowing well
stargard_gt7.mean_flowing_temp = stargard_gt7.temp_flowing(
    gt7_formation.profile, 1, gt7_zenith, 4
)

# Calculate mean water column density in a non-flowing well
stargard_gt7.mean_stat_dens = stargard_gt7.dens_static(
    stargard_gt7.mean_stat_temp, stargard_gt7.salinity
)

# Calculate mean water column density in flowing well
stargard_gt7.mean_flowing_dens = stargard_gt7.dens_dynamic(
    stargard_gt7.mean_flowing_temp, stargard_gt7.salinity
)

# Calculate water level in flowing well
stargard_gt7.water_level = stargard_gt7.water_level(
    stargard_gt7.pumping_input.iloc[:, 3],
    stargard_gt7.mean_flowing_dens,
    probe_depth=272.28,
    atmo_pressure=101325,
)

# Calculate measured drawdown
stargard_gt7.recorded_drawdown = stargard_gt7.measured_drawdown(
    stargard_gt7.water_level
)

# Calculate true water level, after eliminating thermal lift
stargard_gt7.true_water_level = stargard_gt7.true_water_level(
    stargard_gt7.water_level,
    stargard_gt7.mean_flowing_dens,
    stargard_gt7.mean_stat_dens,
    depth_max=2962,
)

# Calculate true drawdown, after eliminating thermal lift
stargard_gt7.true_drawdown = stargard_gt7.true_drawdown(
    stargard_gt7.true_water_level
)

# Save results to file
stargard_gt7.save_results(filename="results.xlsx")

# %% FIGURES
# stargard_gt7.raw_data_plot(
#     stargard_gt7.pumping_input.iloc[:, 0],
#     stargard_gt7.pumping_input.iloc[:, 5],
#     stargard_gt7.pumping_input.iloc[:, 4],
#     stargard_gt7.pumping_input.iloc[:, 3],
#     title="Stargard GT-7 raw data",
# )

stargard_gt7.mosaic_plot(
    stargard_gt7.pumping_input.iloc[:, 0],
    stargard_gt7.pumping_input.iloc[:, 6],
    stargard_gt7.mean_flowing_temp,
    stargard_gt7.mean_flowing_dens,
    stargard_gt7.water_level,
    stargard_gt7.true_water_level,
    stargard_gt7.recorded_drawdown,
    stargard_gt7.true_drawdown,
    bounds=False,
    show_fit=True,
    title="Stargard GT-7",
    figsize=(25, 12),
)
"""
