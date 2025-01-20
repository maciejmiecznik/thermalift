#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Validity: brine_density(t, s) in (kg/m3 ); 0 < t < 180 deg. C; 0 < S < 0.16 kg/kg
Accuracy: ±0.1 %
Reference: H. Sun, R. Feistel, M. Koch and A. Markoe, New equations for density, 
entropy, heat capacity, and potential temperature of a saline thermal fluid, 
Deep-Sea Research, I 55 (2008), 1304–1310.
"""

# correlation parameters
a1 = 9.999E2
a2 = 2.034E-2
a3 = -6.162E-3
a4 = 2.261E-5
a5 = -4.657E-8
b1 = 8.020E2
b2 = -2.001
b3 = 1.677E-2
b4 = -3.060E-5
b5 = -1.613E-5
   
def brine_density(t, ss):
# Below function calculates brine density as a function of temperature [deg. C]
# and salinity, expressed in kg/kg
    if ss<0.35: 
        rho_brine = a1 + a2*t + a3*t**2 + a4*t**3 +a5*t**4 + b1*ss + b2*ss*t + b3*ss*t**2 + b4*ss*t**3 + b5*ss**2*t**2 
    else:
# Below function calculates brine density as a function of temperature [deg. C]
# and salinity, expressed in g/dm3
        s = ss/1050
        for i in range(1,10):
            rho_brine = a1 + a2*t + a3*t**2 + a4*t**3 +a5*t**4 + b1*s + b2*s*t + b3*s*t**2 + b4*s*t**3 + b5*s**2*t**2
            s = ss/rho_brine
    return rho_brine




            
        
                
                
        


    
    
    
