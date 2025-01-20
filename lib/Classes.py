# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 12:23:23 2023
Last update on Monday, Jan 20, 2025

author: Maciej Miecznik
affiliation: Mineral and Energy Economy Research Institute, 
             Polish Academy of Sciences
             Wybickiego 7A, 31-261 Kraków, Poland
e-mail: miecznik@min-pan.krakow.pl

purpose: this code performs calculation to eliminate the effect of thermal
lift from the raw data of recorded wellhead pressure / water level in 
geothermal wells. Records without the noise caused by thermal lift can be
used for better assessment of the true drawdown - hence, for better evaluation
of true reservoir transmissivity (hydraulic characterization)
"""

import brine_density
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# https://stackoverflow.com/questions/67614071/how-to-use-pandas-to-work-on-a-data-loaded-from-my-own-created-class


class Formation():
    def __init__(self, filename):
        self.filename = filename
        
    def temp_interpolation(self, zmin, zmax, dz, n):
        formation = pd.read_csv(self.filename, sep=';', decimal='.')
        
        # Perform n-polynomial fit
        coefficients = np.polyfit(formation.iloc[:, 0], formation.iloc[:, 1], n)
        print('Interpolation coefficients: ', coefficients)
        
        # Create n-polynomial function
        p = np.poly1d(coefficients)
        
        # create 'new' depths points
        depth_new = np.arange(zmin, zmax, dz) 
        temp_pred = p(depth_new)
        return formation, depth_new, temp_pred
    
    def line_plot(self, formation_depth, formation_temp, depth_new, temp_pred):
        fig, axs = plt.subplots(1, figsize = (6,6), layout='constrained')
        axs.plot(temp_pred, depth_new, linewidth = 2, color = 'red', 
                      label = 'interpolation')
        axs.scatter(formation_temp, formation_depth, color = 'orange', 
                       label = 'measurements')
        axs.set_xticks(np.arange(0, formation_temp.max()+5, 5))
        axs.set_yticks(np.arange(0, formation_depth.max()+250, 250))
        axs.invert_yaxis()
        axs.grid(True)
        axs.set_xlabel('Temperature [°C]')
        axs.set_ylabel('Measured depth [m]')
        axs.legend(loc='lower left')
        fig.suptitle('Interpolated temperature along well`s curvature', 
                     fontsize = 12)


class Well():
  
    def __init__(self, df, id = '', name = '', type = '', 
                 salinity = 0.0, tvd = 0.0, md = 0.0):
        self.id = id
        self.df = df
        self.name = name
        self.type = type
        self.salinity = salinity
        self.tvd = tvd
        self.md = md
     
# Calculate mean static temperature in the water column 
# Well not pumped   
# Needs correction, to account for cases with non-uniform temperature distribution
    def temp_static(self, df):
        return df.iloc[:,1].mean() 
    
# Calculate mean temperature in the flowing well
    def temp_flowing(self, df1, n1, df2, n2):
        return (df1.iloc[:,n1].max() + df2.iloc[:,n2])/2 #
    
# Calculate mean water column density in a non-flowing well
    def dens_static(self, temp_static, salinity):
        return brine_density.brine_density(temp_static, salinity) 

# Calculate mean water column density in a flowing well
    def dens_dynamic(self, mean_temp_flowing, salinity):
        return brine_density.brine_density(mean_temp_flowing, salinity) 

# Convert pressure records to water level
    def water_level(self, pressure_level, flow_dens, probe_depth, atmo_pressure):
        water_level = probe_depth - (pressure_level*1E5-atmo_pressure)/(9.81*flow_dens)
        return water_level
    
# Calculate measured drawdown
    def measured_drawdown(self, water_level):
        rec_drawdown = water_level - water_level.min() 
        return rec_drawdown

# Calculate the true water level, after eliminating thermal lift
    def true_water_level(self, water_level, flow_dens, stat_dens, depth_max):
        true_water_level = water_level+(1-flow_dens/stat_dens)*depth_max
        return true_water_level

# Calculate true drawdown, after eliminating thermal lift
    def true_drawdown(self, true_water_level):
        true_drawdown = true_water_level-true_water_level.min()
        return true_drawdown

