#!/usr/bin/env python

"""
@file: Utilities for analyzing a simulation that has already been run. Defines objective for practical purposes.
"""

# workingDir = '/home/jph/Foersteaarsprojekt'
workingDir = '/Users/jonashyatt/Code/Foersteaarsprojekt'
def getWorkingDir():
    return workingDir

# Ensure path is correct.
import os
os.chdir(workingDir)

# Make sure this script can run without a display (server environment).
import matplotlib
matplotlib.use('pdf')
matplotlib.rcParams.update({'font.size': 24})

# Import helper modules
import matplotlib.pyplot as plt
# from matplotlib import mpl
import math
import json
from mcstas_utils import getExperiment, now, getLimits, run_mcstas, compile_mcstas
import numpy as np

# Define size of brilliance data.
resultsFile = "parameter_results.json"
plt.rcParams["figure.figsize"] = (15,8)

def getResultsFile():
    return resultsFile

def read_file(path, filename, row_count = 101, col_count = 4):
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

# Split into pixels and throw into psd array
def read_psd(save_dir, x = 200, y = 200):
    a = []
    with open(save_dir) as f:
        i = 0
        for line in f:
            if not '#' in line:
                a.append([])
                lineArray = line.split(' ')
                for pixel in lineArray:
                    try:
                        float(pixel)
                        a[i].append(float(pixel))
                    except ValueError:
                        'nothing'
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

def getErrors(result, data_source, data_sample):
    # Calculate the error, by error propagation.
    result[2] = math.sqrt((((1 / data_source[1]) ** 2) * (data_sample[2] ** 2)) + ((((data_sample[1]) / ((data_source[1] ** 2)) ** 2) * (data_source[2] ** 2))))
    return result

def process_price(path):
    with open(path + '/price.dat') as f:
        price = int(float(f.readline()))

    return price

def process_brilliance(path, type, row_count = 101, col_count = 4):
    # Read files
    data_begin = read_file(path, '{}_source_brilliance.dat'.format(type))
    data_end = read_file(path, '{}_sample_brilliance.dat'.format(type))

    # Process the files
    # Ignore divide by zero, we'll fix it later
    with np.errstate(divide='ignore', invalid='ignore'):
        comp = np.divide(data_end, data_begin)
        
    result = np.zeros((row_count, col_count))

    # Normalize the data and add correct x axis
    for i in xrange(0, row_count):
        result[i] = fixDivisionByZeroAndIndex(data_begin[i], comp[i])
        getErrors(result[i], data_begin[i], data_end[i])

    # Split and transpose for ease of further calculations.
    res_x = result[:, 0:1].T[0]
    res_y = result[:, 1:2].T[0]
    err_y = result[:, 2:3].T[0]

    # Calculate the area under the curves
    area = np.trapz(y = res_y, x = res_x)
    
    # Return all relevant stuff!
    return [area, result, res_x, res_y, err_y]

def plotPSD(save_dir, xmax = 2, ymax = 2, filename = 0):
    fig, ax = plt.subplots()
    z = read_psd(save_dir)
    dim = len(z[0])
    z = z[0:dim]
    
    x = np.linspace(-xmax, xmax, num = dim)
    y = np.linspace(-ymax, ymax, num = dim)

    plt.pcolor(x, y, z)
    plt.colorbar()
    
    plt.xlabel("X-Position [cm]")
    plt.ylabel("Y-Position [cm]")
    
    plt.title('Intesity as a function of position')
    
    if filename == 0:
        filename = 'psd_{}.png'.format(now())
    plt.savefig(filename)
    
    return filename

def plotDIV(save_dir, xmax = 2, ymax = 2, filename = 0):
    fig, ax = plt.subplots()
    z = read_psd(save_dir)
    dim = len(z[0])
    z = z[0:dim]
    
    x = np.linspace(-xmax, xmax, num = dim)
    y = np.linspace(-ymax, ymax, num = dim)
    
    plt.pcolor(x, y, z)
    plt.colorbar()
    
    plt.xlabel("Horizontal Divergence [degrees]")
    plt.ylabel("Vertical Divergence [degrees]")
    
    plt.title('Intensity as a function of 2d divergence')
    
    if filename == 0:
        filename = 'div_{}.png'.format(now())
    plt.savefig(filename)
    
    return filename

def plotBT(instrument, params):
    # Run sim to get all the required data.
    save_dir = run_mcstas(instrument, params, neutrons = 100000000)
    [mean_area, mean_result, res_x, res_y, err_y] = process_brilliance(save_dir, 'Mean')
    # [peak_area, peak_result, peak_res_x, peak_res_y, peak_err_y] = process_brilliance(save_dir, 'Peak')

    # Plot the data
    fig, ax = plt.subplots()

    # ax.plot(peak_res_x, peak_res_y, 'r.-', label='Peak brilliance transfer')
    ax.plot(res_x, res_y, 'b.-', label='Mean brilliance transfer')

    legend = ax.legend(loc='upper left', shadow=True)

    plt.xlabel("Wavelength [AA]")
    plt.ylabel("Brilliance Transfer")
    plt.title('Mean brilliance transfers as a function of wavelength')
    plt.axis([0, 8, 0, 1])
    plt.grid(True)
    plt.savefig('ess_brill_optimized_mean_{}.png'.format(now()))

    return save_dir

# Negative brilliance is essentially the area under the brilliance transfer curve
# We subtract this from the maximum possible brilliance transfer to get a function we can minimize.
def getNegativeBrilliance(instrument, params):
    save_dir = run_mcstas(instrument, params)
    # price = process_price(save_dir)
    price = 1
    area = process_brilliance(save_dir, 'Mean')[0]

    if (area > 8):
        return area

    return (8 - area) * price

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

    compile_mcstas(getExperiment())
    save_dir = plotBT(getExperiment(), json.loads(lines[-1]))
    plotDIV(save_dir + '/source_div.dat', filename = 'div_before_ess_brill_optimized.png')
    plotDIV(save_dir + '/sample_div.dat', filename = 'div_after_ess_brill_optimized.png')
    
    plotPSD(save_dir + '/source_psd.dat', filename = 'psd_before_ess_brill_optimized.png')
    plotPSD(save_dir + '/sample_psd.dat', filename = 'psd_after_ess_brill_optimized.png')
    
