#!/usr/bin/env python 

import numpy as np
import sys
from tqdm import trange
from optparse import OptionParser
from astropy.io import fits
from matplotlib import pyplot as plt, cm

from datetime import datetime
from casacore import tables
import argparse
from casacore.tables import *

# ---------------------------------------------------------------------------- #
# Simple RFI flagging on MWA MeasurementSets.
# ---------------------------------------------------------------------------- #

plt.rcParams.update({
    "font.size": 10,
    "font.sans-serif": ["Helvetica"]})

cm = 1/2.54

parser = OptionParser(usage = "usage: %prog binfile" + """Simple RFI flagging on MWA measurement set""")
parser.add_option("--obsid", dest="obsid", type="int", help="Obsid to plot")
options, args = parser.parse_args()
	
# Reading in the measurement set.
ta = table(f"{options.obsid}.ms/ANTENNA")
nant = len(ta.getcol("POSITION"))
nbl = (nant/2)*(nant-1)

tf = table(f"{options.obsid}.ms/SPECTRAL_WINDOW")
nchans = len(tf[0]["CHAN_FREQ"])

# Select only the first set of autos so that we can get all the unique times, the number of integrations and the number of polarisations
t = table(f"{options.obsid}.ms")

t1 = taql("select from $t where (ANTENNA1==0) && (ANTENNA2==0)")
nint = len(t1.getcol["TIME"])
first_vis = t1.getcol("DATA", 0, 1)
npol = first_vis.shape[2]

t1 = taql("select from $t where ANTENNA1 != ANTENNA2")

# Read a single visibility to get an idea of how much memory it consumes
firstvis = t1.getcol(data_column, startrow=1, nrow=1)
vis_size = sys.getsizeof(firstvis) * nbl # multiple by the number of baselines because that is the smallest quanta we can read
print("Size of single integration = %d bytes" %(vis_size))
chunk_size = int(max_mem / vis_size) * nbl
if chunk_size > nvis:
    chunk_size = nvis
print("Reading %d visibilities per chunk" %(chunk_size))

# Read visibility data in chunks to avoid utilising too much memory
rms=[]
for row in range(0, nvis, chunk_size):
    print("\nProcessing row %d" %(row))
    nremaining = nvis - row

    print(" - Reading visibilities")
    if nremaining >= chunk_size:
        vis_ant1 = t1.getcol("ANTENNA1", startrow=row, nrow=chunk_size)
        vis_ant2 = t1.getcol("ANTENNA2", startrow=row, nrow=chunk_size)
        vis_data = t1.getcol(data_column, startrow=row, nrow=chunk_size)
        vis_flag = t1.getcol("FLAG", startrow=row, nrow=chunk_size)
        nvis_read = chunk_size
    else:
        vis_ant1 = t1.getcol("ANTENNA1", startrow=row, nrow=nremaining)
        vis_ant2 = t1.getcol("ANTENNA2", startrow=row, nrow=nremaining)
        vis_data = t1.getcol(data_column, startrow=row, nrow=nremaining)
        vis_flag = t1.getcol("FLAG", startrow=row, nrow=nremaining)
        nvis_read = nremaining
    nint_read = int(nvis_read / nbl)
    nvis_all = nvis_read * nchan * npol
    print(" - Read %d integrations; %d visibilities - Flagged = %.1f%%" %(nint_read, nvis_read * nchan * npol, 100.0*np.count_nonzero(vis_flag) / nvis_all))
            
    # Reshape the data
    vis_data = vis_data.reshape((nint_read, nbl, nchan, npol))
    rms.append(np.nanstd(vis_data, axis=1))
    
median=np.nanmedian(rms)
std=np.nanstd(rms)
badchan=[]
bad=[]
err=[]
i=0
for element in rms:    
    if (element>(median+1*std)):
        print(f"Channel {i} has an rms of {element}, flag it.")
        badchan.append(channels[i])
        bad.append(element)
    i=i+1
    
#Plotting the rms values for each channel.
fig = plt.figure(figsize=(20*cm,15*cm))
ax = fig.add_subplot(111)

ax.fill_between(x=tf[0]["CHAN_FREQ"], y1=median-1*std, y2=median+1*std, alpha=0.3, color="grey")
ax.scatter(tf[0]["CHAN_FREQ"], rms, fmt="o", color="darkgreen")
ax.scatter(badchan, bad, yerr=err, fmt="o", color="red")

#ax.plot(channels, medians, '-')
ax.axhline(median, linestyle='--', color='grey')

ax.set_xlim([0, 768])
ax.set_ylabel("RMS")
ax.set_xlabel("Channel")
ax.set_title(f"Channels to be flagged:\n{badchan}")
ax.title.set_color('darkred')

outname = f"{options.obsid}_rms_per_channel.png"
fig.savefig(outname, bbox_inches="tight")
