#!/usr/bin/env python

"""
@file: Utilities for analyzing a simulation that has already been run. Defines objective for practical purposes.
"""

workingDir = '/home/jph/Foersteaarsprojekt'
# workingDir = '/Users/jonashyatt/Code/Foersteaarsprojekt'
def getWorkingDir():
    return workingDir

# Ensure path is correct.
import os
os.chdir(workingDir)

# Make sure this script can run without a display (server environment).
import matplotlib
matplotlib.use('pdf')

# Import helper modules
import matplotlib.pyplot as plt
import json
from mcstas_utils import getExperiment, now, getLimits, run_mcstas
import numpy as np

# Define size of brilliance data.
resultsFile = "parameter_results.json"
row_count = 101
col_count = 4
plt.rcParams["figure.figsize"] = (15,8)

def getResultsFile():
    return resultsFile

def read_file(path, filename):
    a = np.zeros((row_count, col_count))
    with open(path + '/' + filename) as f:
        i = 0
        for line in f:
            if '#' not in line:
                lineArray = line.split(' ')
                a[i][0] = float(lineArray[0])
                a[i][1] = float(lineArray[1])
                a[i][2] = float(lineArray[2])
                a[i][3] = float(lineArray[3])
                i = i + 1
                
    return a

def fixDivisionByZeroAndIndex(row_a, row_comp):
    res = [row_a[0], 0, 0, 0]
    if (row_comp[1] > 0):
        res[1] = row_comp[1]
    
    if (row_comp[2] > 0):
        res[2] = row_comp[2]
        
    if (row_comp[3] > 0):
        res[3] = row_comp[3]
    
    return res

def process_brilliance(path, type):
    # Read files
    data_begin = read_file(path, '{}_brill_begin.dat'.format(type))
    data_end = read_file(path, '{}_brill_end.dat'.format(type))

    # Process the files
    # Ignore divide by zero, we'll fix it later
    with np.errstate(divide='ignore', invalid='ignore'):
        comp = np.divide(data_end, data_begin)
        
    result = np.zeros((row_count, col_count))

    # Normalize the data and add correct x axis
    for i in xrange(0, row_count):
        result[i] = fixDivisionByZeroAndIndex(data_begin[i], comp[i])

    # Split and transpose for ease of further calculations.
    res_x = result[:, 0:1].T[0]
    res_y = result[:, 1:2].T[0]

    # Calculate the area under the curves
    area = np.trapz(y = res_y, x = res_x)
    
    # Return all relevant stuff!
    return [area, result, res_x, res_y]

def plotBT(instrument, params):
    # Run sim to get all the required data.
    save_dir = run_mcstas(instrument, params)
    [mean_area, mean_result, res_x, res_y] = process_brilliance(save_dir, 'Mean')
    [peak_area, peak_result, peak_res_x, peak_res_y] = process_brilliance(save_dir, 'Peak')
    
    # @TODO: Deal with the error propergation here!!!!
    
    # Plot the data
    fig, ax = plt.subplots()

    ax.plot(peak_res_x, peak_res_y, 'r.-', label='Peak brilliance transfer')
    ax.plot(res_x, res_y, 'b.-', label='Mean brilliance transfer')
    
    legend = ax.legend(loc='upper left', shadow=True)
    
    plt.xlabel("Wavelength [AA]")
    plt.ylabel("Brilliance Transfer")
    plt.title('Peak/Mean brilliance transfers as a function of wavelength\nPeak area: {:3.2f}, Mean area: {:3.2f}'.format(peak_area, mean_area))
    plt.axis([0, 8, 0, 1])
    plt.grid(True)
    plt.savefig('optimized_mean_{}.png'.format(now()))
    
    return save_dir

# Negative brilliance is essentially the area under the brilliance transfer curve
# We subtract this from the maximum possible brilliance transfer to get a function we can minimize.
def getNegativeBrilliance(instrument, params):
    save_dir = run_mcstas(instrument, params)
    area = process_brilliance(save_dir, 'Mean')[0]
    
    if (area > 8):
        return area
    
    return 8 - area

# Objective function, takes the arguments from hyperopt and converts to a dict which is run as a simulation.
def objective(args):
    limitsDict = getLimits()
    paramsDict = {}
    i = 0
    for key in limitsDict.keys():
        paramsDict[key] = args[i]
        i += 1

    return getNegativeBrilliance(getExperiment(), paramsDict)

if __name__ == "__main__":
    # get all the plots if this file is run directly.
    with open(getResultsFile(), "rb") as a:
        lines = a.readlines()
    
    save_dir = plotBT(getExperiment(), json.loads(lines[-1]))
