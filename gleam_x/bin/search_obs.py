#!/usr/bin/env python

#Script to identify obsids to download along the Galactic plane.

import matplotlib as mpl
mpl.use("Agg")
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors as mcol
import matplotlib.cm as cm

cm = 1/2.54

import numpy as np
import math
from astropy.io import fits
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import SkyCoord
from glob import glob
import urllib.request
import json
import os
import sys
import argparse
import pandas as pd

BASEURL = "http://ws.mwatelescope.org/"

# 128T -> Compact 01/10/2016
#Compact -> Extended 30/06/2017
#Extended -> Compact 01/09/2018
#Compact -> Extended 04/02/2019
#Extended -> Compact 01/09/2019
#Compact -> Extended 10/10/2020
#Extended -> Compact 03/05/2021
#Compact -> Extended 01/04/2022
#Extended -> Compact 01/04/2023

bounds = [Time("2016-12-01T00:00", scale="utc", format="isot").gps, \
          Time("2017-06-30T00:00", scale="utc", format="isot").gps, \
          Time("2018-09-01T00:00", scale="utc", format="isot").gps, \
          Time("2019-02-04T00:00", scale="utc", format="isot").gps, \
          Time("2019-09-01T00:00", scale="utc", format="isot").gps, \
          Time("2020-10-10T00:00", scale="utc", format="isot").gps, \
          Time("2021-05-03T00:00", scale="utc", format="isot").gps, \
          Time("2022-04-01T00:00", scale="utc", format="isot").gps, \
          Time("2023-04-01T00:00", scale="utc", format="isot").gps]

#Which configuration is used for the obsid?          
def getconfig(obsid, b):
    if (obsid < b[0]): 
       return "PHASE1"
    elif (obsid > b[1] and obsid < b[2]) or \
       (obsid > b[3] and obsid < b[4]) or \
       (obsid > b[5] and obsid < b[6]) or \
       (obsid > b[7] and obsid < b[8]):
       return "EXTENDED"
    else:
       return "COMPACT"

def getmeta(servicetype='metadata', service='obs', params=None):
    """Given a JSON web servicetype ('observation' or 'metadata'), a service name (eg 'obs', find, or 'con')
       and a set of parameters as a Python dictionary, return a Python dictionary containing the result.
    """
    if params:
        # Turn the dictionary into a string with encoded 'name=value' pairs
        data = urllib.parse.urlencode(params)
        data=data.encode('ascii')
        print(data)
    else:
        data = ''

    # Get the data
    try:
        result = json.load(urllib.request.urlopen(BASEURL + servicetype + '/' + service + '?', data=data))
    except urllib.error.HTTPError as err:
        print("HTTP error from server: code=%d, response:\n %s" % (err.code, err.read()))
        return
    except urllib.error.URLError as err:
        print("URL or network error: %s" % err.reason)
        return

    # Return the result dictionary
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group1 = parser.add_argument_group("Input/output files")
    group1.add_argument("--resume", dest='resume', type=int, default=1,
                        help="Page to resume from, in case of timeout (default = 1)")
    group1.add_argument("--mintime", dest='mintime', type=int, default=1060000000,
                        help="minimum GPS starttime for search (default = 1060000000)")
    group1.add_argument("--maxtime", dest='maxtime', type=int, default=1334003000,
                        help="maximum GPS starttime for search (default = 1334003000)")
    #group1.add_argument("--minlat", dest='minlat', type=int, default=-20,
    #                    help="minimum Galactic latitude for search (default = -10)")
    #group1.add_argument("--maxlat", dest='maxlat', type=int, default=20,
    #                    help="maximum Galactic latitude for search (default = 10)")
    #group1.add_argument("--minlon", dest='minlon', type=int, default=70,
    #                    help="minimum Galactic longitude for search (default = 70)")
    #group1.add_argument("--maxlon", dest='maxlon', type=int, default=290,
    #                    help="maximum Galactic longitude for search (default = 290)")
    group1.add_argument("--minra", dest='minra', type=int, default=250,
                        help="minimum Right ascension for search (default = 250)")
    group1.add_argument("--maxra", dest='maxra', type=int, default=300,
                        help="maximum Right ascension for search (default = 300)")
    group1.add_argument("--mindec", dest='mindec', type=float, default=-55,
                        help="minimum Declination for search (default = -55)")
    group1.add_argument("--maxdec", dest='maxdec', type=float, default=-60,
                        help="maximum Declination for search (default = -60)")
    group1.add_argument("--chan", dest='chan', type=int, default=121,
                        help="frequency channel for search (default = 121)")
    group1.add_argument("--output_G", dest='output_G', type=str, default="GLEAM.txt",
                        help="Input/output text file for search results for GLEAM (default = GLEAM.txt")
    group1.add_argument("--output_GX", dest='output_GX', type=str, default="GLEAM-X.txt",
                        help="Input/output text file for search results for GLEAM-X (default = GLEAM-X.txt")
    group1.add_argument("--overwrite", dest='overwrite', action='store_true', default=False,
                        help="Overwrite text file instead of reusing it")
    results = parser.parse_args()

# Try all observations for specified channel
# Within 10 deg of the plane
# Excluding HEX config

obsids_GX = []
nobs_GX = []
ras_GX = []
decs_GX = []
durations_GX = []
ls_GX = []
bs_GX = []

obsids_G = []
nobs_G = []
ras_G = []
decs_G = []
durations_G = []
ls_G = []
bs_G = []

if not os.path.exists(results.output_G and results.output_GX):
    p = results.resume
    n = 100
    while n == 100:
        olist = getmeta(service='find', params={ \
            'mintime': results.mintime, \
            'maxtime': results.maxtime, \
            'mode': "HW_LFILES", \
            'projectid': "G0008", \
            'cenchan': results.chan, \
            #'mingal_long': results.minlon, \
            #'maxgal_long': results.maxlon, \
            'mingal_lat': -5, \
            'maxgal_lat': 5, \
            'minra': results.minra, \
            'maxra': results.maxra, \
            'mindec': results.mindec, \
            'maxdec': results.maxdec, \
            'dataquality': "1", \
            'pagesize' : 100, \
            'page' : p, \
            'dict':1})

        print(olist)
        n = len(olist)
        p += 1
        count=0
        for obs in olist:
            config = getconfig(obs['mwas.starttime'], bounds)
            if config == "EXTENDED":
                ras_GX.append(obs['sm.ra_pointing'])
                decs_GX.append(obs['sm.dec_pointing'])
                ls_GX.append(obs['sm.gal_long'])
                bs_GX.append(obs['sm.gal_lat'])
                obsids_GX.append(obs['mwas.starttime'])
                durations_GX.append(obs['mwas.stoptime']-obs['mwas.starttime'])
                count=count+1
            elif config == "PHASE1":
                ras_G.append(obs['sm.ra_pointing'])
                decs_G.append(obs['sm.dec_pointing'])
                ls_G.append(obs['sm.gal_long'])
                bs_G.append(obs['sm.gal_lat'])
                obsids_G.append(obs['mwas.starttime'])
                durations_G.append(obs['mwas.stoptime']-obs['mwas.starttime'])
                count=count+1
        print(count)
    # Stupid lists vs numpy array indexing
    obsids_GX = np.array(obsids_GX)
    ras_GX = np.array(ras_GX)
    decs_GX = np.array(decs_GX)
    durations_GX = np.array(durations_GX)
    ls_GX = np.array(ls_GX)
    bs_GX = np.array(bs_GX)

    obsids_G = np.array(obsids_G)
    ras_G = np.array(ras_G)
    decs_G = np.array(decs_G)
    durations_G = np.array(durations_G)
    ls_G = np.array(ls_G)
    bs_G = np.array(bs_G)
else:
    arr_GX = np.loadtxt(results.output_GX, dtype="float32", skiprows=1)
    arr_GX = arr_GX.T
    obsids_GX, durations_GX, ras_GX, decs_GX, ls_GX, bs_GX = arr_GX[0], arr_GX[1], arr_GX[2], arr_GX[3], arr_GX[4], arr_GX[5]

    arr_G = np.loadtxt(results.output_G, dtype="float32", skiprows=1)
    arr_G = arr_G.T
    obsids_G, durations_G, ras_G, decs_G, ls_G, bs_G = arr_G[0], arr_G[1], arr_G[2], arr_G[3], arr_G[4], arr_G[5]

locs_GX = SkyCoord(ras_GX, decs_GX, unit = (u.deg, u.deg), frame='fk5')
locs_G = SkyCoord(ras_G, decs_G, unit = (u.deg, u.deg), frame='fk5')
#freq = 1.28*results.chan

if results.overwrite is True or not(os.path.exists(results.output_GX)):
    np.savetxt(results.output_GX, np.array([obsids_GX, durations_GX, ras_GX, decs_GX, locs_GX.galactic.l.wrap_at('180d').deg, locs_GX.galactic.b.deg]).T, fmt="%d %f %f %f %f %f", header="obsids duration ra dec l b")
if results.overwrite is True or not(os.path.exists(results.output_G)):
    np.savetxt(results.output_G, np.array([obsids_G, durations_G, ras_G, decs_G, locs_G.galactic.l.wrap_at('180d').deg, locs_G.galactic.b.deg]).T, fmt="%d %f %f %f %f %f", header="obsids duration ra dec l b")

fig = plt.figure(figsize=(20.0*cm,16.0*cm))
ax = fig.add_subplot(111)
ax.set_xlabel("Galactic longitude $l$ ($^\circ$)")
ax.set_ylabel("Galactic latitude $b$ ($^\circ$)")
ax.scatter(locs_GX.galactic.l.deg, locs_GX.galactic.b.deg, color="magenta", edgecolors='black', marker='v', label='GLEAM-X')
ax.scatter(locs_G.galactic.l.deg, locs_G.galactic.b.deg, color="yellow", edgecolors='black', label='GLEAM')
ax.legend(loc='center right', bbox_to_anchor=(0.65, 1.05), ncol=2, fancybox=True, shadow=True)
ax.invert_xaxis()
fig.savefig("Pointings.png", bbox_inches="tight")
fig.savefig("Pointings.pdf", bbox_inches="tight")

fig2 = plt.figure(figsize=(20.0*cm,16.0*cm))
ax2 = fig2.add_subplot(111)
ax2.set_xlabel("Right ascension $Ra$ ($^\circ$)")
ax2.set_ylabel("Declination $Dec$ ($^\circ$)")
ax2.scatter(ras_GX, decs_GX, color="magenta", edgecolors='black', marker='v', label='GLEAM-X', s=35.0)
ax2.scatter(ras_G, decs_G, color="yellow", edgecolors='black', label='GLEAM', alpha=0.5, s=25.0)
ax2.legend(loc='center right', bbox_to_anchor=(0.35, 1.05), ncol=2, fancybox=True, shadow=True)
ax2.invert_xaxis()
#ax2.set_aspect('equal')
ax2.set_title(f'Number of pointings= {len(ras_G)} + {len(ras_GX)}', loc='center')
fig2.savefig("J2000_pointings.png", bbox_inches="tight")
fig2.savefig("J2000_pointings.pdf", bbox_inches="tight")
