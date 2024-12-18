#!/usr/bin/env python

from __future__ import print_function
__author__ = "Silvia Mantovanini"
__date__ = "10/12/2024"

import sys
import numpy as np
from argparse import ArgumentParser 
from astropy.io import fits
from astropy.coordinates import EarthLocation, SkyCoord
from astropy import units as u
from scipy.interpolate import griddata

def calc_weight(weight, output):
    with fits.open(weight) as hdu:
        data = hdu[0].data
        header = hdu[0].header
    
    # Find indices of non-NaN and NaN data points
    y, x = np.indices(data.shape)
    nonnan_mask = ~np.isnan(data)
    nan_mask = np.isnan(data)

    points = np.column_stack((x[nonnan_mask], y[nonnan_mask]))
    values = data[nonnan_mask]
    nan_points = np.column_stack((x[nan_mask], y[nan_mask]))

    # Interpolate NaN values
    region_mask = (nan_points[:, 0] >= 4500) & (nan_points[:, 0] < 15000) & \
                  (nan_points[:, 1] >= 5000) & (nan_points[:, 1] < 8400)
    nan_inside = nan_points[region_mask]

    # Interpolate NaN values
    interpolated_values = griddata(
        points, values, nan_inside, method='linear', fill_value=np.nan
    )

    for (x_coord, y_coord), value in zip(nan_inside, interpolated_values):
        data[y_coord, x_coord] = value 

    hdu = fits.PrimaryHDU(data, header=header)
    hdu.writeto(output, overwrite=True)

    return output

if __name__ == '__main__':
    parser = ArgumentParser(description="""
    The Galactic centre and a few other areas along the plane have been assigned with NULL weight from swarp
    This script returns the ideal weight for those regions so that they're not flagged out in the mosaic.
    """)
    
    group1 = parser.add_argument_group("required arguments:")
    group1.add_argument("--weight", type=float, help="The WEIGHT assigned by swarp to your mosaic")
    group1.add_argument("--output", type=float, help="The output name for the new WEIGHT map")

    options = parser.parse_args()

    new_weight_map = calc_weight(options.weight, options.output)
