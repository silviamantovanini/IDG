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

uvd = UVData()
uvd.read(f'{results.obsid}.ms')

out_prefix=f'{results.directory}'

withoriginal =  uvd.flag_array.astype(int).sum(axis=(1,3))
plt.imshow(withoriginal, aspect='auto', cmap=cm.plasma)
plt.savefig(f'{out_prefix}/with_original.png')
