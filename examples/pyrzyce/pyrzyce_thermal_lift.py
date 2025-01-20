# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 14:44:31 2024

@author: miecznik
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys
# adding lib folder to the system path
sys.path.insert(0, '..\..\lib')
import Classes

# filename = '..\..\lib\dummy.txt'
# file_df = pd.read_csv(filename)



# %% Import data

# Import static temperature profile of the formation, Pyrzyce GT-1 BIS well
formation_temperature_file = 'pyrzyce_gt1bis_static_temperature.csv'
gt1bis_formation = pd.read_csv(formation_temperature_file, decimal='.', sep=',')


#########################################################################
# Import pumping data from Pyrzyce GT-1 BIS well
#gt1bis_data = pd.read_excel('system_readings_5_min_utf_8_expanded.xlsx', usecols=[3, 4,5, 6])

# Data filtering: only measurement points between 20.02.2024 9:00 and 16.03.2024 23:00
#gt1bis_data = gt1bis_data[(gt1bis_data['data i czas']>'2024-02-20 09:00:00') & (gt1bis_data['data i czas']<='2024-03-16 23:00:00')]

#########################################################################