# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 11:56:13 2024

@author: miecznik
"""

# %% Import libraries
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# adding lib folder to the system path
sys.path.insert(0, '..\..\lib')
import Classes



# %% Import static temperature profile of the formation 
#Stargard GT-6 well
formation_temperature_file = 'stargard_gt6_static_temperature.csv'
gt6_form_temperature = Classes.Formation(formation_temperature_file)
gt6_form_temperature.profile = gt6_form_temperature.temp_interpolation(0, 3000, 50, 2)
gt6_form_temperature.line_plot(gt6_form_temperature.profile[0].iloc[:,0], 
                                    gt6_form_temperature.profile[0].iloc[:,1], 
                                    gt6_form_temperature.profile[1], 
                                    gt6_form_temperature.profile[2])


# Import pumping data from Stargard GT-6 well, Zenith probe ######
gt6_zenith = pd.read_csv('zenith_measerements.csv', sep=';', decimal=',')

# Removes duplicate columns with measurement date and time
gt6_zenith = gt6_zenith.drop(columns=['ST3_SC_GT6_1_TempWej - Czas',
                                      'ST3_SC_GT7_1_CisnWej - Czas', 
                                      'ST3_SC_GT7_1_TempWej - Czas', 
                                      'ST1_FIT_GT6_1_Wart - Czas', 
                                      'ST2_FIT_GT7_1_Wart - Czas']) 

# Changing column names to shorter ones
gt6_zenith.rename(columns={'ST3_SC_GT6_1_CisnWej - Czas': 'time', 
                           'ST3_SC_GT6_1_CisnWej': 'gt6_pressure', 
                           'ST3_SC_GT6_1_TempWej': 'gt6_temperature',
                           'ST3_SC_GT7_1_CisnWej': 'gt7_pressure', 
                           'ST3_SC_GT7_1_TempWej': 'gt7_temperature', 
                           'ST1_FIT_GT6_1_Wart': 'gt6_flow', 
                           'ST2_FIT_GT7_1_Wart': 'gt7_flow'}, 
                  inplace=True)

# Converting a time column (type: string) to type 'datetime64[ns]
gt6_zenith['time'] = pd.to_datetime(gt6_zenith['time'], 
                                    errors='raise', 
                                    dayfirst=True)

# Data filtering: only measurement points before the gt6_zenith probe failure
gt6_zenith = gt6_zenith[gt6_zenith['time']<='2023-06-20 08:00:00']

#########################################################################


# %% Create Well class object and perform calculations
stargard_gt6 = Classes.Well(gt6_zenith)

# Add properties to the object
stargard_gt6.salinity = 121

# Calculate mean static temperature in the wellbore
stargard_gt6.mean_stat_temp = stargard_gt6.temp_static(gt6_form_temperature.profile)
"""
# Calculate mean dynamic temperature in the flowing well
stargard_gt6.mean_flowing_temp = stargard_gt6.temp_flowing(gt6_form_temperature, gt6_zenith)

# Calculate mean water column density in a non-flowing well
stargard_gt6.mean_stat_dens = stargard_gt6.dens_static(stargard_gt6.mean_stat_temp, stargard_gt6.salinity)

# Calculate mean water column density in flowing well
stargard_gt6.mean_flowing_dens = stargard_gt6.dens_dynamic(stargard_gt6.mean_flowing_temp, stargard_gt6.salinity)

# Calculate water level in flowing well
stargard_gt6.water_level = stargard_gt6.water_level(stargard_gt6.df.iloc[:,3], stargard_gt6.mean_flowing_dens, probe_depth=270.82, atmo_pressure=101325 )

# Calculate measured drawdown
stargard_gt6.recorded_drawdown = stargard_gt6.measured_drawdown(stargard_gt6.water_level)

# Calculate true water level, after eliminating thermal lift
stargard_gt6.true_water_level = stargard_gt6.true_water_level(stargard_gt6.water_level, stargard_gt6.mean_flowing_dens, stargard_gt6.mean_stat_dens, depth_max=2962)

# Calculate true drawdown, after eliminating thermal lift
stargard_gt6.true_drawdown = stargard_gt6.true_drawdown(stargard_gt6.true_water_level)


# %% Polyfit function
def polyfit(x, y, deg):
    idx = np.isfinite(x) & np.isfinite(y) # exclude values that are NaN or infinity
    return np.polyfit(x[idx], y[idx], deg)

# Calculate polynomial fitting between the flowrate and the drawdown
rec_drawdown_polyfit = polyfit(stargard_gt6.df.iloc[:,6], stargard_gt6.recorded_drawdown, 2)
true_drawdown_polyfit = polyfit(stargard_gt6.df.iloc[:,6], stargard_gt6.true_drawdown, 2)


# %% FIGURES
################################ FIGURES ################################

fig1, ax = plt.subplot_mosaic(
    [['flowrate', 'drawdawn_vs_flowrate'],
     ['temperature', 'drawdawn_vs_flowrate'],
     ['density', 'drawdawn_vs_flowrate'],
     ['water_level', 'drawdawn_vs_flowrate'],
     ['drawdown', 'drawdawn_vs_flowrate']],
    layout='constrained', width_ratios=[2, 1.3], figsize=(25,12))

ax['flowrate'].plot(stargard_gt6.df.iloc[:,0], stargard_gt6.df.iloc[:,6], c='blue', label='flow rate')
ax['flowrate'].grid(True)
ax['flowrate'].set_ylabel('Flow rate [$m^3$/h]', fontsize=12)
ax['flowrate'].legend(loc='lower left')

ax['temperature'].plot(stargard_gt6.df.iloc[:,0], stargard_gt6.mean_flowing_temp, c='red', label='mean temperature in flowing well')
ax['temperature'].grid(True)
ax['temperature'].set_ylabel('Temperature [°C]', fontsize=12)
ax['temperature'].legend(loc='lower left')
ax['temperature'].sharex(ax['flowrate'])

ax['density'].plot(stargard_gt6.df.iloc[:,0], stargard_gt6.mean_flowing_dens, c='orange', label='mean density in flowing well')
ax['density'].grid(True)
ax['density'].set_ylabel('Density[kg/$m^3$]', fontsize=12)
ax['density'].legend(loc='lower left')
ax['density'].sharex(ax['flowrate'])

ax['water_level'].plot(stargard_gt6.df.iloc[:,0], stargard_gt6.water_level, c='violet', label='water level')
ax['water_level'].plot(stargard_gt6.df.iloc[:,0], stargard_gt6.true_water_level, c='purple', label='true water level')
ax['water_level'].grid(True)
ax['water_level'].set_ylabel('Water level [m b.g.l.]', fontsize=12)
ax['water_level'].invert_yaxis()
ax['water_level'].legend(loc='lower left')
ax['water_level'].sharex(ax['flowrate'])

ax['drawdown'].plot(stargard_gt6.df.iloc[:,0], stargard_gt6.recorded_drawdown, c='dodgerblue', label='recorded drawdown')
ax['drawdown'].plot(stargard_gt6.df.iloc[:,0], stargard_gt6.true_drawdown, c='navy', label='true drawdown')
ax['drawdown'].grid(True)
ax['drawdown'].set_ylabel('Drawdown [m]', fontsize=12)
ax['drawdown'].invert_yaxis()
ax['drawdown'].legend(loc='lower left')
ax['drawdown'].sharex(ax['flowrate'])

ax['drawdawn_vs_flowrate'].scatter(stargard_gt6.df.iloc[:,6], stargard_gt6.recorded_drawdown, c='dodgerblue', label='recorded drawdown')
ax['drawdawn_vs_flowrate'].plot(np.arange(0, 260, 5), np.polyval(rec_drawdown_polyfit, np.arange(0, 260, 5)), c='red', linewidth = 3, label='recorded drawdown fit')
ax['drawdawn_vs_flowrate'].text(150, 20, 's = {:1.2e}*Q^2 + {:1.2e}*Q + {:2.2f}'.format(rec_drawdown_polyfit[0], rec_drawdown_polyfit[1], rec_drawdown_polyfit[2]), fontsize=11, color='red', weight='bold')
ax['drawdawn_vs_flowrate'].scatter(stargard_gt6.df.iloc[:,6], stargard_gt6.true_drawdown, c='navy', label='true drawdown')
ax['drawdawn_vs_flowrate'].plot(np.arange(0, 260, 5), np.polyval(true_drawdown_polyfit, np.arange(0, 260, 5)), c='blue', linewidth = 3, label='true drawdown fit')
ax['drawdawn_vs_flowrate'].text(40, 10, 's = {:1.2e}*Q^2 + {:1.2e}*Q + {:2.2f}'.format(true_drawdown_polyfit[0], true_drawdown_polyfit[1], true_drawdown_polyfit[2]), fontsize=11, color='blue', weight='bold')
ax['drawdawn_vs_flowrate'].grid(True)
ax['drawdawn_vs_flowrate'].set_ylim(0, 150)
ax['drawdawn_vs_flowrate'].invert_yaxis()
ax['drawdawn_vs_flowrate'].set_xlabel('Flow rate [$m^3$/h]', fontsize=12)
ax['drawdawn_vs_flowrate'].set_ylabel('Drawdown [m]', fontsize=12)
ax['drawdawn_vs_flowrate'].legend(loc='lower left')

plt.suptitle('Production well in north-western Poland', fontsize=16)
plt.show()
plt.savefig('Stargard_gt6_thermal_lift.png', dpi=300)

# Export results for Lumpfit++ modeling
# Creat dataframe for export
stargard_gt6_lumpfit = pd.DataFrame()
stargard_gt6_lumpfit['time'] = stargard_gt6.df['time']
stargard_gt6_lumpfit['gt6_drawdown'] = stargard_gt6.true_water_level
stargard_gt6_lumpfit['gt6_flow'] = stargard_gt6.df['gt6_flow']

# Reducing and averaging
gt6_time_reduced = np.convolve(stargard_gt6_lumpfit['time'].to_numpy()+stargard_gt6_lumpfit['time'].to_numpy()[-1], [.5,.5], mode='valid')[::2]
gt6_drawdown_reduced = np.convolve(stargard_gt6_lumpfit['gt6_drawdown'].to_numpy()+stargard_gt6_lumpfit['gt6_drawdown'].to_numpy()[-1], [.5,.5], mode='valid')[::2]
gt6_flow_reduced = np.convolve(stargard_gt6_lumpfit['gt6_flow'].to_numpy()+stargard_gt6_lumpfit['gt6_flow'].to_numpy()[-1], [.5,.5], mode='valid')[::2]
"""