#!/usr/bin/env python

#Flagging RFI using SSINS

import os
import json

from SSINS import Catalog_Plot as cp, util as ssins_util
from SSINS import SS, INS, MF, plot_lib
from matplotlib import pyplot as plt, cm
import numpy as np
import pylab
from pyuvdata import UVData, UVFlag, utils as uvutils
import sys
import shlex
import shutil
import argparse
from casacore.tables.table import table

parser = argparse.ArgumentParser()
group1 = parser.add_argument_group("Input/output files")
group1.add_argument("--obsid", dest='obsid', type=int, help="Obsid to flag")
group1.add_argument("--directory", dest='directory', type=str, help="Path to directory where obsid is saved")
results = parser.parse_args()

ss = SS()
print('Reading the obsid to flag as a ss object')
ss.read(f'{results.obsid}.ms', read_data=True, diff=True, file_type='ms')
ss.apply_flags(flag_choice='original')
ins_cross = INS(ss, spectrum_type='cross')

shape_dict = {}
sig_thresh = 7 #{shape:  for shape in shape_dict}
#sig_thresh['narrow'] = 7
#sig_thresh['streak'] = 8

mf = MF(
    ins_cross.freq_array,
    sig_thresh,
    shape_dict=shape_dict,
    streak=False,
    narrow=True
)
ins_cross.metric_array[ins_cross.metric_array == 0] = np.ma.masked
ins_cross.metric_ms = ins_cross.mean_subtract()
ins_cross.sig_array = np.ma.copy(ins_cross.metric_ms)
mf.apply_match_test(ins_cross)

out_prefix=f'{results.directory}'
with open(f'{out_prefix}/flags.json', "w") as events_file:
    events_obj = [
        {
            'time_bounds': [int(event[0].start), int(event[0].stop)],
            'freq_bounds': [int(event[1].start), int(event[1].stop)],
            'shape': event[2],
            'sig': event[3] if event[3] is None else float(event[3])
        } for event in ins_cross.match_events
    ]
    json.dump(events_obj, events_file, indent=4)

occ =  ss.flag_array.astype(int).sum(axis=(1,3))
plt.imshow(occ, aspect='auto', cmap=cm.plasma)
plt.savefig(f'{out_prefix}/occ_pre.png')

ins_cross.mask_to_flags()
len(np.unique(ss.time_array))

print('Reading file as a UVData object')
uvd = UVData()
uvd.read(f'{results.obsid}.ms')

uvf = UVFlag(uvd, waterfall=True, mode='flag')
uvf = ins_cross.flag_uvf(uvf)
uvutils.apply_uvflag(uvd, uvf) # This is a pyuvdata utility function that safely applies flags to UVData from UVFlag

print("Writing new ms")
uvd.write_ms(f'{out_prefix}/{results.obsid}_flagged.ms')

postocc =  uvd.flag_array.astype(int).sum(axis=(1,3))
plt.imshow(postocc, aspect='auto', cmap=cm.plasma)
plt.savefig(f'{out_prefix}/occ_post.png')
