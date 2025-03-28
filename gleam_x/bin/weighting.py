#! /usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy import stats,ndimage
from astropy.coordinates import SkyCoord
from scipy.interpolate import interp2d, RectBivariateSpline, interpn, griddata
from argparse import ArgumentParser

def create_weightmap(rms):
    rms_fits = fits.open(rms)
    valid_mask = np.isfinite(rms_fits[0].data)
    imshape_zeros = np.zeros(valid_mask.shape)
    imshape_zeros[valid_mask] = 1.

    if args.do_mask is True: 
        dist_to_edge = ndimage.distance_transform_edt(imshape_zeros,sampling=[100,100])
        edgemask = dist_to_edge <= np.nanmax(dist_to_edge)/5

        lowercut = np.nanquantile(rms_fits[0].data, 0.45)
        uppercut = np.nanquantile(rms_fits[0].data,0.95)
        rms_mask = rms_fits[0].data <= lowercut
        rms_mask2 = rms_fits[0].data >= uppercut

        combined_rms = np.logical_or(rms_mask,rms_mask2)
        combined_mask = np.logical_and(combined_rms,edgemask)
        rms_fits[0].data[combined_mask] = np.nan 
     
    weightmap = (1/(rms_fits[0].data**2))

    return weightmap


if __name__ == "__main__":
    parser = ArgumentParser(
        description="create a weighting for an IDG down-weighting the edge of the image. "
    )
    parser.add_argument(
        "rmsfits",
        help="RMS map to use the weighting on and produce final weightmap thats input for swarp"
    )
    parser.add_argument(
        "outfits",
        help="Outfile to save the map to"
    )
    parser.add_argument(
        "--mask",
        action="store_true",
        default=False,
        dest="do_mask",
        help="Add a mask for the edges of the weightmap"
    )
    args = parser.parse_args()
    
    weightmap = create_weightmap(args.rmsfits)
    fits.writeto(args.outfits, weightmap, overwrite=True)
