#!/usr/bin/env python

# Read in the PSF map
# FInd all the areas which are Galactic latitude less than 4 degrees
# INterpolate the PSF
# Write out the new map

# Then when I rerun the flux-calibration, using the PSF map, it should be correct

import numpy as np
from astropy.io import fits
from astropy import wcs
from optparse import OptionParser
from astropy.coordinates import SkyCoord
from astropy import units as u
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

usage="Usage: %prog [options] <file>\n"
parser = OptionParser(usage=usage)
parser.add_option('--psf',type="string", dest="psf",
                    help="The filename of the psf image you want to read in.")
parser.add_option('--output',type="string", dest="output", default="interpolated_GP_PSF.fits",
                    help="The filename of the output interpolated PSF image.")
(options, args) = parser.parse_args()

# Read in the PSF
psf = fits.open(options.psf)
a = psf[0].data[0]
b = psf[0].data[1]
pa = psf[0].data[2]
blur = psf[0].data[3]

w_psf = wcs.WCS(psf[0].header,naxis=2)

# create an array but don't set the values (they are random)
indexes = np.empty( (psf[0].data.shape[1]*psf[0].data.shape[2],2),dtype=int)

idx = np.array([ (j,0) for j in range(psf[0].data.shape[2])])
j=psf[0].data.shape[2]
for i in range(psf[0].data.shape[1]):
    idx[:,1]=i
    indexes[i*j:(i+1)*j] = idx

# The RA and Dec co-ordinates of each location in the PSF map
# Each one is a 1D array of shape 64800 (from 180 (Dec) x 360 (RA))
ra_psf,dec_psf = w_psf.wcs_pix2world(indexes,1).transpose()
# A 1D array of co-ordinates at each location
c_psf = SkyCoord(ra=ra_psf, dec=dec_psf, unit=(u.degree, u.degree))

# A 1D list of indices referring to the locations where we want to use the data
gal_indices = np.where(abs(c_psf.galactic.b.value) > 4.)

# A 1D list of pairs of co-ordinates ("points") referring to the locations where we want to use the data
gin = gal_indices[0]
idx = indexes[gin[:]]
a_data = a[idx[:,1], idx[:,0]]
b_data = b[idx[:,1], idx[:,0]]
pa_data = pa[idx[:,1], idx[:,0]]
blur_data = blur[idx[:,1], idx[:,0]]

grid_x, grid_y = np.mgrid[0:179:180j, 0:359:360j]

# Only interpolate over points which are not NaN
a_cubic_interp = griddata(idx[a_data!=np.isnan], a_data[a_data!=np.isnan], (grid_y, grid_x), method="linear")
b_cubic_interp = griddata(idx[b_data!=np.isnan], b_data[b_data!=np.isnan], (grid_y, grid_x), method="linear")
pa_cubic_interp = griddata(idx[pa_data!=np.isnan], pa_data[pa_data!=np.isnan], (grid_y, grid_x), method="linear")
blur_cubic_interp = griddata(idx[blur_data!=np.isnan], blur_data[blur_data!=np.isnan], (grid_y, grid_x), method="linear")


psf[0].data[0] = a_cubic_interp
psf[0].data[1] = b_cubic_interp
psf[0].data[2] = pa_cubic_interp
psf[0].data[3] = blur_cubic_interp

psf.writeto(options.output,overwrite=True)
