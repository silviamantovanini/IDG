#!/usr/bin/env python

from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np
import sys

in_xx = sys.argv[1]
in_yy = sys.argv[2]
in_rms = sys.argv[3]
out_weight = sys.argv[4]

hdu_xx = fits.open(in_xx)
hdu_yy = fits.open(in_yy)
hdu_rms = fits.open(in_rms)

try:
    bscale = hdu_rms[0].header["BSCALE"]
except IndexError:
    bscale = 1.0

stokes_I = (hdu_xx[0].data + hdu_yy[0].data) / 2.0
shape = np.array(hdu_rms[0].data.shape)
cen = shape // 2
delta = np.ceil(shape * 0.05).astype(np.int)

# Mask the Galactic plane from the rms image to exclude from the calculation:
wcs = WCS(hdu_rms[0].header)

region = hdu_rms[0].data[ cen[0] - delta[0] : cen[0] + delta[0], cen[1] - delta[1] : cen[1] + delta[1] ]

ny, nx = region.shape
y_indices, x_indices = np.mgrid[ (cen[0] - delta[0]) : (cen[0] + delta[0]), (cen[1] - delta[1]) : (cen[1] + delta[1]) ]

ra, dec = wcs.pixel_to_world(x_indices, y_indices).ra.deg, wcs.pixel_to_world(x_indices, y_indices).dec.deg
coords = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame="fk5")
galactic_coords = coords.galactic
b = galactic_coords.b.deg

mask = np.abs(b) > 4
valid_pixels = region[mask]

# Use a central region of the RMS map to calculate the weight via inverse variance
cen_rms = bscale * np.nanmean(valid_pixels)
#cen_rms = bscale * np.nanmean(
#    hdu_rms[0].data[
#        cen[0] - delta[0] : cen[0] + delta[0], cen[1] - delta[1] : cen[1] + delta[1],
#    ]
#)

weight = stokes_I ** 2 / cen_rms ** 2
hdu_xx[0].data = weight
hdu_xx.writeto(out_weight)
