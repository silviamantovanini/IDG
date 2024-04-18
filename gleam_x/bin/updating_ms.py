#!/usr/bin/env python

#Updating .ms with missing elements from the original .ms

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

cvd=table(f"../{results.obsid}_flagged.ms",readonly=False)

#cvd.putkeyword("MWA_SUBBAND", "Table: {}/{}.ms/MWA_SUBBAND").format(results.directory, results.obsid)
#cvd.putkeyword("MWA_TILE_POINTING", "Table: {}/{}.ms/MWA_TILE_POINTING").format(results.directory, results.obsid)

#cvd.putkeyword('MWA_SUBBAND', f'Table: {results.directory}/{results.obsid}_flagged.ms/MWA_SUBBAND')
#cvd.putkeyword('MWA_TILE_POINTING', f'Table: {results.directory}/{results.obsid}_flagged.ms/MWA_TILE_POINTING')

cvd.putkeyword('MWA_SUBBAND', 'Table: MWA_SUBBAND')
cvd.putkeyword('MWA_TILE_POINTING', 'Table: MWA_TILE_POINTING')

cvd.getkeywords()
#For future reference
#cvd.getkeywords()
#cvd.removekeyword("MWA_TILE_POINTING")
