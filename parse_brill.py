#!/usr/bin/env python

import sys
import numpy as np
import matplotlib.pyplot as plt

row_count = 101
col_count = 4

def read_file(filename):
    a = np.zeros((row_count, col_count))
    with open(sys.argv[1] + filename) as f:
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

# Read files
mean_begin = read_file('Mean_brill_begin.dat')
peak_begin = read_file('Peak_brill_begin.dat')

mean_end = read_file('Mean_brill_end.dat')
peak_end = read_file('Peak_brill_end.dat')

# Process the files
peak_comp = np.divide(peak_end, peak_begin)
mean_comp = np.divide(mean_end, mean_begin)

peak_result = np.zeros((row_count, col_count))
mean_result = np.zeros((row_count, col_count))

for i in xrange(0, row_count):
    peak_result[i] = compare(peak_begin[i], peak_comp[i])
    mean_result[i] = compare(mean_begin[i], mean_comp[i])

# Plot results
fig, axarr = plt.subplots(2)

axarr[0].plot(peak_result[:, 0:1].T[0], peak_result[:, 1:2].T[0])
axarr[0].set_title('Peak')
axarr[0].set_autoscale_on(False)
axarr[0].axis([0.5, 8, 0, 1])
# axarr[0].ylabel('Brilliance Transfer')
# axarr[0].xlabel('Wavelength [AA]')

axarr[1].plot(mean_result[:, 0:1].T[0], mean_result[:, 1:2].T[0])
axarr[1].set_title('Mean')
axarr[1].set_autoscale_on(False)
axarr[1].axis([0.5, 8, 0, 1])
# axarr[1].ylabel('Brilliance Transfer')
# axarr[1].xlabel('Wavelength [AA]')

fig.tight_layout()
plt.xlabel("Wavelength [AA]")
plt.ylabel("Brilliance Transfer")
plt.show()




