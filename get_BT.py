import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt

import os
import subprocess
import time
import sys
from mcstas_utils import run_mcstas, compile_mcstas, now
from simulation_analysis_utils import process_brilliance

matplotlib.rcParams.update({'font.size': 30})

#from parse_brill import run_mcstas

# params = {u'guide_loutxw': 7.885643934926492, u'guide_mid_height': 0.07004703010787484, u'guide_linxw': 52.318252906787734, u'guide_linyh': 31.176145777453176, u'guide_mid_width': 0.08534642073016357, u'guide_loutyh': 5.29370802141684}

params = {'guide_loutxw': 7.236909136827689, 'guide_mid_height': 0.07242770304915397, 'guide_linxw': 73.11127655966307, 'guide_linyh': 5.924279652618898, 'guide_mid_width': 0.05851273883218753, 'guide_loutyh': 1.9432886941931304}

# compile_mcstas('ess_sim_simple')
# save_dir = run_mcstas('ess_sim_simple', params, neutrons = 100000000)
save_dir = './data/ess_sim_simple_148949502936168'
res = process_brilliance(save_dir, 'Mean')

# print len(res)

# Plot results
fig, ax = plt.subplots()
# ax.plot(peak_res_x, peak_res_y, 'r-', label='Peak brilliance transfer')
ax.errorbar(res[2], res[3], yerr=res[4], label='Mean brilliance transfer')
legend = ax.legend(loc='upper left', shadow=True)

plt.xlabel("Wavelength [AA]")
plt.ylabel("Brilliance Transfer")
# plt.title('Peak/Mean brilliance transfers as a function of wavelength\nPeak area: {}, Mean area: {}'.format(area_peak, area_mean))
plt.axis([0, 8, 0, 1])
plt.grid(True)
plt.savefig('optimized_mean_4.png')

