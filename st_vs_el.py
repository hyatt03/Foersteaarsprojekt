#!/usr/bin/env python

"""
@file: This script compares straight and elliptical guides
"""

# Make sure this script can run without a display (server environment).
import matplotlib
matplotlib.use('pdf')
matplotlib.rcParams.update({'font.size': 24})

# Import helper modules
import matplotlib.pyplot as plt
import numpy as np

import os
import subprocess
import time
import sys
import functools
from multiprocessing.dummy import Pool as ThreadPool
from mcstas_utils import run_mcstas, compile_mcstas, now
from simulation_analysis_utils import process_brilliance

plt.rcParams["figure.figsize"] = (15,8)
instrument_name = 'st_vs_el'

def run_single(which):
    params = {
        'elip': 0
    }

    if which == 1:
        params['elip'] = 1

    return run_mcstas(instrument_name, params, neutrons = 100000000)


def parrallel_run_simulation():
    pool = ThreadPool(2)
    # dirs = pool.map(run_single, [1, 2])
    dirs = ['./data/st_vs_el_148948323747645', './data/st_vs_el_148948323747666']

    # Plot the data
    fig, ax = plt.subplots()
    mean_results_elip = process_brilliance(dirs[0], 'Mean')
    mean_results_str =  process_brilliance(dirs[1], 'Mean')
    ax.errorbar(mean_results_elip[2], mean_results_elip[3], label='Mean brilliance transfer elliptical', yerr = mean_results_elip[4])
    ax.errorbar(mean_results_str[2], mean_results_str[3], label='Mean brilliance transfer straight', yerr = mean_results_str[4])
    
    legend = ax.legend(loc='upper left', shadow=True)
    
    plt.xlabel("Wavelength [AA]")
    plt.ylabel("Brilliance Transfer")
    plt.title('Mean brilliance transfers as a function of wavelength')
    plt.axis([0, 8, 0, 1])
    plt.grid(True)
    plt.savefig('st_vs_elip_{}.png'.format(now()))
        
    # ax.plot(peak_res_x, peak_res_y, 'r.-', label='Peak brilliance transfer')    

compile_mcstas(instrument_name)
parrallel_run_simulation()
