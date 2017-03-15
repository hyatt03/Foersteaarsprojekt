#!/usr/bin/env python

"""
@file: In this file some helper methods for running McStas within python.
"""

import os
import subprocess
import time
import sys

FNULL = open(os.devnull, 'w')
limitsDict = {
    'mid_xw_e1': [0, 0.1],
    'mid_yh_e1': [0, 0.1],
    'mid_xw_e2': [0, 0.1],
    'mid_yh_e2': [0, 0.1],
    'linxw_e1': [0, 10],
    'loutxw_e1': [0, 1e6],
    'linyh_e1': [0, 10],
    'loutyh_e1': [0, 1e6],
    'linxw_e2': [0, 100],
    'loutxw_e2': [0, 100],
    'linyh_e2': [0, 100],
    'loutyh_e2': [0, 100],
    'cguide_ma': [1, 6],
    'cguide_mi': [1, 6],
    'cguide_ms': [1, 6],
    'cguide_radius': [2000, 3000],
    'cguide_length': [1, 10],
    'cguide_xw': [0, 0.1],
    'cguide_yh': [0, 0.1]#,
#    'a2_e1': [0.0001, 0.0006],
#    'a2_e2': [0.0001, 0.0006],
}

def getExperiment():
    return 'ess_brill_optimized'

def getLimits():
    return limitsDict

def now():
    return int(time.time() * 100000)

# Compiles an instrument to a binary file.
def compile_mcstas(instrument):
    workingDir = getWorkingDir()
    print 'About to compile {}'.format(instrument)
    
    compile_to_c = ['mcstas', '-I', '.', '-t', '-o', '{}/{}.c'.format(workingDir, instrument), '{}/{}.instr'.format(workingDir, instrument)]
    print 'Running: {}'.format(compile_to_c)
    exc = subprocess.call(compile_to_c, stdout=FNULL, stderr=subprocess.STDOUT)
    if exc == 0:
        print 'Compiled to C!'
    else:
        print 'Compile to C failed!'
        sys.exit(1)

    compile_to_bin = ['cc', '-o', '{}/{}.out'.format(workingDir, instrument), '{}/{}.c'.format(workingDir, instrument), '-lm']
    print 'running: {}'.format(compile_to_bin)
    exc = subprocess.call(compile_to_bin, stdout=FNULL, stderr=subprocess.STDOUT)
    if exc == 0:
        print 'Compiled to binary!'
    else:
        print 'Compile to binary failed!'
        sys.exit(1)
        
    return exc

# runs a simulation given a set of parameters
def run_mcstas(instrument, params, neutrons = 10000000, m_val = 2):
    workingDir = getWorkingDir()
    epoch_time = now()
    save_dir = '{}/data/{}_{}'.format(workingDir, instrument, epoch_time)
    
    # Create a command array, include default parameters
    run_instrument_with_params = [
        '{}/{}.out'.format(workingDir, instrument), 
        '-n', str(neutrons), 
        '-d', save_dir
    ]

    if (instrument == 'ess_brill_optimized'):
        run_instrument_with_params.append('sample_size=0.01')
        run_instrument_with_params.append('benchmark=0')
        run_instrument_with_params.append('guide_start=2')
        run_instrument_with_params.append('guide_rotation_angle=0')
        run_instrument_with_params.append('length_e1=4')
        run_instrument_with_params.append('guide_start_xw=0.1')
        run_instrument_with_params.append('guide_start_yh=0.1')
    
    for key in params.keys():
        run_instrument_with_params.append('{}={}'.format(key, params[key]))

    exc = subprocess.call(run_instrument_with_params, stdout=FNULL, stderr=subprocess.STDOUT)
    if exc == 0:
        print 'Successful run!'
    else:
        print 'Something went wrong!'
        sys.exit(1)
    
    print 'finished running in {}'.format(now() - epoch_time)
        
    return save_dir

# Resolve circular dependencies
from simulation_analysis_utils import getWorkingDir
