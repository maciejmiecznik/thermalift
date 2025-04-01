# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 15:01:30 2025

@author: miecznik
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
def temp_interpolation(formation_temp_file, zmin, zmax, dz, tolerance):
    formation_temp_file = "formation_temperature.csv"
    formation = pd.read_csv(formation_temp_file, sep=";", decimal=".")

    # create 'new' depths points
    depth_new = np.arange(zmin, zmax, dz)

    formation_new = pd.merge(formation[:, 0], depth_new, how="outer")
    # formation_new.insert(1, "Temperature", np.nan)

    return formation, formation_new
"""

formation_temp_file = "formation_temperature.csv"
formation = pd.read_csv(formation_temp_file, sep=";", decimal=".")

# create 'new' depths points
depth_new = pd.Series(np.arange(0, 3000, 30), name=formation.columns[0])

formation_new = pd.merge(
    formation, depth_new, on=formation.columns[0], how="outer"
)
formation_new.interpolate(method="cubic", inplace=True)
formation_new.dropna(axis=0, inplace=True)

print(
    "Average temperature of the formation before interpolation was ",
    formation["Temp"].mean(),
)
print(
    "Average temperature of the formation after interpolation is ",
    formation_new["Temp"].mean(),
)

fig, axs = plt.subplots(1, figsize=(8, 8))
axs.scatter(formation["Depth"], formation["Temp"], s=40, color="blue")
axs.plot(formation_new["Depth"], formation_new["Temp"], c="red")
plt.show()
