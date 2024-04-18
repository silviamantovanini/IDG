#!/usr/bin/env python

#Determine rms for each channel and report the ones that need to be flagged.

import os
import json
import numpy as np
import sys
import shutil
import argparse

from optparse import OptionParser
from astropy.io import fits
from matplotlib import pyplot as plt, cm

plt.rcParams.update({
    "font.size": 10,
    "font.sans-serif": ["Helvetica"]})

cm = 1/2.54

parser = OptionParser(usage = "usage: %prog binfile" + """Difference time-based calibration solutions to determine ionspheric variation""")
parser.add_option("--obsid", dest="obsid", type="int", help="Obsid to plot")
options, args = parser.parse_args()

#Determining mean, median and standard deviation values for each rms file
files = os.listdir(os.curdir)

mean=[]
median=[]
std=[]
channels=[]
for i in range(0,767):
    if i in range(0,9):
        file = f'{options.obsid}_shallow-000{i}-image_rms.fits'
        hdu=fits.open(file)
        data=hdu[0].data
        test=np.nanmedian(data)
    if i in range(10,99):
        file = f'{options.obsid}_shallow-00{i}-image_rms.fits'
        hdu=fits.open(file)
        data=hdu[0].data
        test=np.nanmedian(data)
    if i in range(100,767):
        file = f'{options.obsid}_shallow-0{i}-image_rms.fits'
        hdu=fits.open(file)
        data=hdu[0].data
        test=np.nanmedian(data)
    if test != 0:
        mean.append(np.nanmean(data))
        median.append(np.nanmedian(data))
        std.append(np.nanstd(data))
        channels.append(i)

medians=np.nanmedian(median)
stds=np.nanstd(median)
print(f"The std of the rmss is: {stds}")
badchan=[]
bad=[]
err=[]
i=0
for element in median:
    if (element>(medians+1*stds)):
        print(f"Channel {i} has an rms of {element}, flag it.")
        badchan.append(channels[i])
        bad.append(element)
        err.append(std[i])
    i=i+1
  
print(f"The final list of channels to be flagged for {options.obsid} is: {badchan}")

#Plotting the rms values for each channel.
fig = plt.figure(figsize=(20*cm,15*cm))
ax = fig.add_subplot(111)

ax.fill_between(x=channels, y1=medians-1*stds, y2=medians+1*stds, alpha=0.3, color="grey")
ax.errorbar(channels, median, yerr=std, fmt="o", color="darkgreen")
ax.errorbar(badchan, bad, yerr=err, fmt="o", color="red")

#ax.plot(channels, medians, '-')
ax.axhline(medians, linestyle='--', color='grey')

ax.set_xlim([0, 768])
ax.set_ylabel("Median +/- 1sigma")
ax.set_xlabel("Channel")
ax.set_title(f"Channels to be flagged:\n{badchan}")
ax.title.set_color('darkred')

outname = f"{options.obsid}_rms_per_channel.png"
fig.savefig(outname, bbox_inches="tight")
