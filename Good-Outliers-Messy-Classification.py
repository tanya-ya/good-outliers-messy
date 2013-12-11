# -*- coding: utf-8 -*-
"""Good-Outliers-Messy-Classification.py 

This program aims to classify time series into 
good = 'well-behaved', 
good_with_outliers = 'well-behaved' once outliers are removed, and 
messy = all the rest,
where 'well-behaved' either grows linearly or stays roughly constant.

WARNING: the program is designed for visualizing time series;
it actually outputs the graphs of all the time series into files!
File output may be suppressed by --suppress (or -s) option. 
In addition, the classifcation of the time series by names outputs 
into result.txt file. 

The expected data format is a comma-separated .csv with the 
first row representing time coordinates (e.g., years) and 
subsequent rows  - the corresponding time series with 
empty entries for missing values
The first column is reserved for the names of time series
e.g,
,2000,2010
series1,,152
series2,125,136

Two criteria are used: 
- the determination coefficient (DT) or R^2,
- 'spread' = dispersion index-like quantity on the residuals; 
spread behaves resonably well when values of time-series span across 
different timescales.

If DT>=0.9, time series is 'well-behaved' (the threshold can be adjusted). 
However, for points arranged on a horizontal line, DT=0, so near-constant 
behaviour is not classified as 'well-behaved' by the determination coefficient.
In orded to overcome this, we evaluate the residuals with respect to 
the least square fit (after removal of outliers, if any) 
and compute the 'spread':
spread = std(residuals)/sqrt(mean(data))
We set the threshold for the 'spread' to be <0.1.

First the program performs linear regression fit, finds DT and spread. 
If DT>0.9 or spread<0.1, we classify data as Good (='well-behaved').

Then the program attempts to find outliers with respect to Theil-Sen estimator,
which is less sensitive to outliers than the least square fit.

Theil-Sen estimator is computed as follows:
slope: m = median of the slopes for pairs of points
intercept: b = median of the values yi − mxi

All points that fall outside 1.5IQ range from the Theil-Sen estimator 
are considered as outliers.

After removing the outliers, we perform the linear regression fit again 
and compute the DT and the spread.

If DT>0.9 or spread<0.1, we classify data as Good with Outliers.

For our particular data in det_coef_row.csv, 
historical data from years 1980 to 2000 often behaves as outliers

The last attempt is made to remove data from years 1980 to 2000 and see if this 
removal produces a good fit. 

If DT>0.9 or spread<0.1, we classify data as Good with Outliers

In all other situations we classify data as Messy

The program performs reasonably well with respect to the det_coef_row.csv data 
derived from the UNECE statistical database. """

import numpy as np
from scipy import stats
import csv
from plot_data_into_files import plot_data_with_outliers, plot_data
import math
import shutil
import os
import argparse

#read threshold values for DT and spread from command line
#DEFAULT: DT_threshold = 0.9, spread_threshold = 0.1
parser = argparse.ArgumentParser()
parser.add_argument('DT_threshold', nargs='?', default=0.9, type=float, 
                    help='optional: threshold value for DT')
parser.add_argument('spread_threshold', nargs='?', default=0.1, type=float,
                    help='optional: threshold value for spread')
parser.add_argument('-s', '--suppress', help='to suppress plotting', 
                    action='store_true')
args = parser.parse_args()

DT_threshold = args.DT_threshold
spread_threshold = args.spread_threshold

print 'DT_threshold = ', DT_threshold
print 'spread_threshold = ', spread_threshold

#path directories for output

datapath = os.getcwd()
path = datapath + '/good-outliers-messy'

if not args.suppress: #if not request for suppressed output
    #try creating good-outliers-messy directory (if doesn't exist)
    try: 
        os.mkdir(path)
    except:
        pass    

    #try to remove previously made subdirectories in that directory (in any)
    try:
        shutil.rmtree(path + '/good')
    except: 
        pass
    
    try:    
        shutil.rmtree(path + '/good_with_outliers')
    except:
        pass

    try:                
        shutil.rmtree(path + '/messy')
    except: 
        pass


    #make new directories
    os.mkdir(path + '/good')
    os.mkdir(path + '/good_with_outliers')
    os.mkdir(path + '/messy')

#set figure counters to 0
good = []
good_with_outliers = []
messy = []
failed = [] #to catch empty rows or other data errors

#read the data and execute the program
with open(datapath + '/det_coef_row.csv','rb') as csvfile:
    reader=csv.reader(csvfile) 
    
    #read first row which contains the range of years
    allyears = reader.next()
    name = allyears.pop(0) #remove (redundant) first element
    allyears = map(int, allyears)

    #analyze the remaining rows of data
    for row in reader:
        name = row.pop(0) #read the name of the data series
        datarow = []
        years = [] #years for this data
        for i in range(1, len(row)):
            try:
                datarow.append(float(row[i].replace(',','')))
                years.append(allyears[i])   
            except ValueError: 
                pass 
                 
        years = np.array(years)
        years_copy = years.copy()
        datarow = np.array(datarow)
        datarow_copy = datarow.copy()
        
        #Least Square Fit + correlation coefficient, etc
        #determination coefficient = r_value^2
        try: 
            slope, intercept, r_value, p_value, std_err = \
                              stats.linregress(years,datarow)
        except: 
            #error: ignore, write to failed, and continue
            failed.append(name)
            continue            
        
        #compute residuals and spread
        ls_residuals = datarow - slope*years - intercept       
        spread = np.std(ls_residuals)/math.sqrt(np.mean(datarow))
        
        #check if satisfies thresholds; proceed with further analysis otherwise
        if r_value**2>DT_threshold or spread<spread_threshold:
            good.append(name)
            if not args.suppress:
                filename = path + '/good/series' + name + '.jpg'           
                plot_data(filename, name, 
                          years, datarow, 
                        slope, intercept, 
                         r_value, spread)
                             
        else:
            #Theil-Sen estimator
            slopes = []
            intercepts = []
            for i in range(len(datarow)):
                for j in range(i+1, len(datarow)):
                    slopes.append((datarow[j] - datarow[i])/(years[j] - years[i]))
            m = np.median(slopes)
            for i in range(len(datarow)):
                intercepts.append(datarow[i] - m*years[i])
            b = np.median(intercepts)
            
            #find outliers with respect to Theil-Sen estimator
            outliers = []
            outlier_years = []
                    
            residuals = datarow - m*years - b
            #quantiles are 0.26 (instead of 0.25) and 0.74 (instead of 0.75) 
            #are chosen to deal with too short time-series
            quantiles = stats.mstats.mquantiles(residuals, prob=[0.26,0.5,0.74])
            bottom_threshold = quantiles[0]-(quantiles[2]-quantiles[0])
            top_threshold = quantiles[2]+(quantiles[2]-quantiles[0])
            for k in range(len(datarow)):
                if (residuals[k]<bottom_threshold
                    or residuals[k]>top_threshold) \
                    and datarow[k] not in outliers:
                    outliers.append(datarow[k])
                    outlier_years.append(years[k])
            
            #remove outliers (if any)
            for outlier in outliers:
                index=np.where(datarow==outlier)
                years = np.delete(years, index[0])
                datarow = np.delete(datarow,index[0])   
                
            #least squares fitting + correlation coefficient, etc
            slope, intercept, r_value, p_value, std_err = \
                                         stats.linregress(years,datarow)                  
                    
            ls_residuals = datarow - slope*years - intercept
            spread = np.std(ls_residuals)/math.sqrt(np.mean(datarow))
            
            if r_value**2 >DT_threshold or spread<spread_threshold:
                good_with_outliers.append(name)
                if not args.suppress:
                    filename = path + '/good_with_outliers/series' + \
                                                     name + '.jpg'              
                    plot_data_with_outliers(filename, name, years, datarow, 
                                         slope, intercept, r_value, spread, 
                                       outlier_years, outliers, years_copy)
                                                             
            else:
                #try removing historical data; otherwise - messy                   
                #remove data with years < 2000 and fit again    
                years2000 = []
                datarow2000 = []
                oldyears = []
                olddata = []
                for i in range(len(years_copy)):
                    if years_copy[i]>2000:
                        years2000.append(years_copy[i])
                        datarow2000.append(datarow_copy[i])
                    else:
                        oldyears.append(years_copy[i])
                        olddata.append(datarow_copy[i])     
                if len(years2000) > 2: 
                    years2000=np.array(years2000)
                    datarow2000=np.array(datarow2000)
                    slope2000, intercept2000, r_value2000, p_value2000, \
                          std_err2000 = stats.linregress(years2000,datarow2000)
                    
                    new_residuals2000 = \
                              datarow2000 - slope2000*years2000 - intercept2000      
                    spread2000 = \
                       np.std(new_residuals2000)/math.sqrt(np.mean(datarow2000))
                    
                    if r_value2000**2 > DT_threshold \
                       or spread2000<spread_threshold: 
                        #removing old data fixes the problem
                        good_with_outliers.append(name)
                        if not args.suppress:
                            filename = path + '/good_with_outliers/series' + \
                                                             name + '.jpg'                        
                            plot_data_with_outliers(filename, name, 
                                             years2000, datarow2000, 
                                           slope2000, intercept2000, 
                                            r_value2000, spread2000, 
                                                  oldyears, olddata, 
                                                         years_copy) 
                        continue                          
                            
                #if we are here, removing old data did not help  
                messy.append(name) 
                if not args.suppress:          
                    filename = path + '/messy/series' + name + '.jpg'
                    plot_data_with_outliers(filename, name, years, datarow, 
                                         slope, intercept, r_value, spread,  
                                       outlier_years, outliers, years_copy)

f = open(datapath + '/result.txt','w')
f.write('Good \n' + str(good) + '\n Good with outliers \n' + str(good_with_outliers) + 
        '\n Messy \n' + str(messy) + '\n Failed \n' + str(failed))
f.close()

