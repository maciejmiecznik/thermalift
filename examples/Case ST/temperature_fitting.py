# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 15:40:03 2025

@author: miecznik
"""

import pandas as pd
import matplotlib.pyplot as plt

data_incomplete = pd.read_excel("Stargard_formation_temp_data_incomplete.xlsx")

data_interpolated = data_incomplete.copy(deep=True)

data_interpolated["MD"] = data_interpolated["MD"].interpolate(method="linear")
data_interpolated["TEMP"] = data_interpolated["TEMP"].interpolate(
    method="slinear"
)

print(data_interpolated.head(10))

f1 = plt.figure()
# f2 = plt.figure()
ax1 = f1.add_subplot(111)
ax1.plot(data_interpolated["TEMP"], data_interpolated["MD"])
ax1.plot(data_interpolated["TEMP"], data_interpolated["TVD"])
ax1.grid(True)
ax1.invert_yaxis()

# ax2 = f2.add_subplot(111)
# ax2.plot(data_interpolated["MD"], data_interpolated["TVD"])
# ax2.invert_yaxis()

plt.show()
