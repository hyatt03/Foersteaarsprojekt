#!/usr/bin/env python

import sys
import numpy as np
import matplotlib.pyplot as plt
import os
import subprocess
import time
from multiprocessing.dummy import Pool as ThreadPool
import functools

from hyperopt import hp

FNULL = open(os.devnull, 'w')

plt.rcParams["figure.figsize"] = (15,8)

row_count = 101
col_count = 4

def read_file(path, filename):
    a = np.zeros((row_count, col_count))
    with open(path + '/' + filename) as f:
        i = 0
        for line in f:
            if '#' not in line:
                a[i][0] = float(line.split(' ')[0])
                a[i][1] = float(line.split(' ')[1])
                a[i][2] = float(line.split(' ')[2])
                a[i][3] = float(line.split(' ')[3])
                i = i + 1
    return a

def compare(row_a, row_comp):
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
    # data_begin = read_file('./brill_ref', '{}_brill_begin.dat'.format(type))

    data_begin = read_file(path, '{}_brill_begin.dat'.format(type))
    data_end = read_file(path, '{}_brill_end.dat'.format(type))

    # Process the files
    # Ignore divide by zero, we'll fix it later
    with np.errstate(divide='ignore', invalid='ignore'):
        comp = np.divide(data_end, data_begin)
        
    result = np.zeros((row_count, col_count))

    # Normalize the data and add correct x axis
    for i in xrange(0, row_count):
        result[i] = compare(data_begin[i], comp[i])

    # Split and transpose for ease of further calculations.
    res_x = result[:, 0:1].T[0]
    res_y = result[:, 1:2].T[0]

    # Calculate the area under the curves
    area = np.trapz(y = res_y, x = res_x)
    
    # Return all relevant stuff!
    return [area, result, res_x, res_y]

def compile_mcstas(instrument):
    print 'About to optimize {}'.format(instrument)
    
    compile_to_c = ['mcstas', '-I', '.', '-t', '-o', './{}.c'.format(instrument), './{}.instr'.format(instrument)]
    print 'Running: {}'.format(compile_to_c)
    exc = subprocess.call(compile_to_c, stdout=FNULL, stderr=subprocess.STDOUT)
    if exc == 0:
        print 'Compiled to C!'
    else:
        print 'Compile to C failed!'
        sys.exit(1)
    
    compile_to_bin = ['cc', '-o', './{}.out'.format(instrument), './{}.c'.format(instrument), '-lm']
    print 'running: {}'.format(compile_to_bin)
    exc = subprocess.call(compile_to_bin, stdout=FNULL, stderr=subprocess.STDOUT)
    if exc == 0:
        print 'Compiled to binary!'
    else:
        print 'Compile to binary failed!'
        sys.exit(1)
        
def run_mcstas(instrument, params):
    epoch_time = int(time.time() * 100000)
    save_dir = './data/{}_{}'.format(instrument, epoch_time)
    print 'Beginning run @ {}'.format(epoch_time)
    
    run_instrument_with_params = [
        './{}.out'.format(instrument), 
        '-n', '10000000', 
        '-d', save_dir,
        'm_val=2',
        'guide_mid_width={}'.format(params['guide_mid_width']),
        'guide_mid_height={}'.format(params['guide_mid_height']),
        'guide_linxw={}'.format(params['guide_linxw']),
        'guide_loutxw={}'.format(params['guide_loutxw']),
        'guide_linyh={}'.format(params['guide_linyh']),
        'guide_loutyh={}'.format(params['guide_loutyh'])
    ]
    
    # print 'running: {}'.format(instrument)
    exc = subprocess.call(run_instrument_with_params, stdout=FNULL, stderr=subprocess.STDOUT)
    if exc == 0:
        print 'Successful run!'
    else:
        print 'Something went wrong!'
        sys.exit(1)
    
    print 'finished running in {}'.format(int(time.time() * 100000) - epoch_time)
        
    return process_brilliance(save_dir, 'Mean')

def optimize_param(instrument, params, parameter_state, initial_area, param):
    dx = parameter_state[param]
    if dx < 10e-5:
        dx = - params[param] / 10

    params[param] += dx
    area, result, res_x, res_y = run_mcstas(instrument, params)
    if (area > initial_area):
        parameter_state[param] = dx * 2
    else:
        parameter_state[param] = dx * 0.3
        
    # print 'Optimizing {} by {} which gives: {}'.format(param, dx, area)
    return [area, dx]

def optimize(instruments, params, area):
    parameter_keys = params.keys()
    params_dx = params.copy()
    for key in parameter_keys:
        params_dx[key] = params_dx[key] / 10
    
    pool = ThreadPool(len(parameter_keys))
    
    for i in xrange(0, 100):
        bound_optimizer = functools.partial(optimize_param, instruments, params.copy(), params_dx, area)
        results = pool.map(bound_optimizer, parameter_keys)

        max_area = area
        for idx in xrange(0, len(parameter_keys)):
            result = results[idx]
            parameter = parameter_keys[idx]
        
            if (result[0] > area):
                max_area = result[0]
                params[parameter] += result[1]
    
        area = max_area
        print 'new params!', params

def getNegativeBrilliance(instrument, params):
    area, b, c, d = run_mcstas(instrument, params)
    if (area > 8):
        return area
    
    return 8 - area

def getSearchSpace(parameterLimits):
    space = {}
    for key in parameterLimits.keys():
        space[key] = hp.uniform(key, parameterLimits[key][0], parameterLimits[key][1]))
        
    return space

# Get initial parameters
parameter_dict_a = {
    'guide_mid_width': 0.02, # 0.18,
    'guide_mid_height': 0.02, # 0.18,
    'guide_linxw': 2, # 10.5,
    'guide_loutxw': 2, # 10.5,
    'guide_linyh': 2, # 10.5,
    'guide_loutyh': 2 # 10.5
}

parameter_dict_b = {
    'guide_mid_width': 0.1,
    'guide_mid_height': 0.05,
    'guide_linxw': 11,
    'guide_loutxw': 10.5,
    'guide_linyh': 11,
    'guide_loutyh': 10.5
}

limitsDict = {
    'guide_mid_width': [0, 0.1],
    'guide_mid_height': [0, 0.1],
    'guide_linxw': [0, 80],
    'guide_loutxw': [0, 80],
    'guide_linyh': [0, 80],
    'guide_loutyh': [0, 80]
}

print getSearchSpace(limitsDict)

# compile_mcstas('ess_sim_simple')
# area, res, res_x, res_y = run_mcstas('ess_sim_simple', parameter_dict_b)
# optimize('ess_sim_simple', parameter_dict, area)

"""
# Plot results
fig, ax = plt.subplots()
# ax.plot(peak_res_x, peak_res_y, 'r-', label='Peak brilliance transfer')
ax.plot(res_x, res_y, 'b-', label='Mean brilliance transfer')
# legend = ax.legend(loc='upper left', shadow=True)

plt.xlabel("Wavelength [AA]")
plt.ylabel("Brilliance Transfer")
# plt.title('Peak/Mean brilliance transfers as a function of wavelength\nPeak area: {}, Mean area: {}'.format(area_peak, area_mean))
plt.axis([0, 8, 0, 1])
plt.grid(True)
plt.show()
"""





