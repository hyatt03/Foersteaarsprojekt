#!/usr/bin/env python

"""
@file: In this file some helper methods for running McStas within python.
"""

import os
import subprocess
import time

FNULL = open(os.devnull, 'w')
limitsDict = {
    'guide_mid_width': [0, 0.1],
    'guide_mid_height': [0, 0.1],
    'guide_linxw': [0, 80],
    'guide_loutxw': [0, 80],
    'guide_linyh': [0, 80],
    'guide_loutyh': [0, 80]
}

def getExperiment():
    return 'ess_sim_simple'

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
    print('About to run! Saving to {}'.format(save_dir))

    run_instrument_with_params = [
        '{}/{}.out'.format(workingDir, instrument), 
        '-n', str(neutrons), 
        '-d', save_dir,
        'm_val={}'.format(m_val)
    ]
    
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

from simulation_analysis_utils import getWorkingDir
