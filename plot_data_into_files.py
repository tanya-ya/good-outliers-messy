"""This module consists of two functions to plot 
time series data and time series data with outliers 
into files, given:
filename
data
slope and intercept for linear regression line
correlation coefficient and 'spread' values (for plot labels)
outlier_years and outlier values (for data with outliers only)
range of all years (for axis range and labeling purposes; outlier case only)"""

import numpy as np
import matplotlib.pyplot as plt
import math


def plot_data_with_outliers(filename, name, years, datarow, 
                        slope, intercept, r_value, spread, 
                     outlier_years, outliers, years_copy):
       
    ax = plt.subplot(111)                  
    plt.plot(years, datarow, 'bo',
             outlier_years, outliers, 'ro', 
             years_copy, slope*years_copy+intercept, 'g-')          
    
    plt.title('Time series ' + name)    

    #set y-limits (+/- sqrt(mean) from the mean)
    datarow_mean = np.mean(datarow) 
    
    if outliers != []:
        minimum = min(np.min(datarow), np.min(outliers), 
                      datarow_mean - math.sqrt(datarow_mean))
        maximum = max(np.max(datarow), np.max(outliers), 
                      datarow_mean + math.sqrt(datarow_mean)) 
    else:    
        minimum = min(np.min(datarow), datarow_mean - math.sqrt(datarow_mean))
        maximum = max(np.max(datarow), datarow_mean + math.sqrt(datarow_mean)) 
    
    #change minimum and maximum to include full markers
    difference = maximum - minimum    
    minimum = minimum - 0.05*difference
    maximum = maximum + 0.05*difference                                              
                                   
    plt.ylim((minimum, maximum)) 
    plt.xlim((np.min(years_copy)-1,np.max(years_copy)+1))        
    
    #labels
    
    plt.text(0.4, 0.2, 'DT =' + str(r_value**2), 
         transform=ax.transAxes, # axes coordinates
         ma='right', ha='right', size=12)
    plt.text(0.4, 0.1, 'Spread =' + str(spread), 
         transform=ax.transAxes, # axes coordinates
         ma='right', ha='right', size=12)              
         
    #place ticks
    
    step = int(math.ceil((max(years_copy)-min(years_copy)+1)/12.))
    ticksyears = range(min(years_copy), max(years_copy)+1,step)
    stryears = map(str, ticksyears)                     
    plt.xticks(ticksyears, stryears)
    
    plt.savefig(filename, bbox_inches='tight', pad_inches=0) 
    plt.close()    
      

def plot_data(filename, name, years, datarow, 
          slope, intercept, r_value, spread):
       
    ax = plt.subplot(111)                  
    plt.plot(years, datarow, 'bo', 
             years, slope*years+intercept, 'g-')
    plt.title('Time series ' + name)          
    
    #set y-limits (+/- sqrt(mean) from the mean)
    datarow_mean = np.mean(datarow) 
    minimum = min(np.min(datarow), datarow_mean - math.sqrt(datarow_mean))
    maximum = max(np.max(datarow), datarow_mean + math.sqrt(datarow_mean))                      
    
    #change minimum and maximum to include full markers
    difference = maximum - minimum    
    minimum = minimum - 0.05*difference
    maximum = maximum + 0.05*difference 
    
    plt.ylim((minimum, maximum))         
    plt.xlim((np.min(years)-1,np.max(years)+1))
      
    
    plt.text(0.4, 0.2, 'DT =' + str(r_value**2), 
         transform=ax.transAxes, # axes coordinates
         ma='right', ha='right', size=12)
    plt.text(0.4, 0.1, 'Spread =' + str(spread), 
         transform=ax.transAxes, # axes coordinates
         ma='right', ha='right', size=12)   
         
    #place ticks
    
    step = int(math.ceil((max(years)-min(years)+1)/12.))
    ticksyears = range(min(years), max(years)+1,step)
    stryears = map(str, ticksyears)                     
    plt.xticks(ticksyears, stryears)
    
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.1) 
    plt.close()      


