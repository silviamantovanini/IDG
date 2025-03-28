#! /usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy import stats,ndimage
from astropy.coordinates import SkyCoord
from astropy import units as u
from scipy.interpolate import interp2d, RectBivariateSpline, interpn, griddata
from argparse import ArgumentParser

from joblib import Parallel, delayed

def sigmoid(x, ref_x):
    return 1. / (1. + np.exp(-(x-ref_x)))

def create_sigweight(infits):
    img_fits = fits.open(infits)
    data = img_fits[0].data
    
    data = np.squeeze(data)
    # Ensure data is at least 2D and select the last two dimensions
    if data.ndim > 2:
        data = data[-2:, :, :]
    elif data.ndim < 2:
        raise ValueError("Data has fewer than 2 dimensions.")
    
    img_shape = data.shape[-2:] # Only consider the last two axes
    valid_mask = np.isfinite(data)
    step = 50
    y, x = np.indices([s//step + 2 for s in img_shape], dtype=np.int32)

    x_grid = np.clip(x*step, None, img_shape[1]-1)
    y_grid = np.clip(y*step, None, img_shape[0]-1)

    print('Image shape: ', img_shape)
    print('Max Indicies:', np.max(y_grid), np.max(x_grid))
    print('Min Indicies:', np.min(y_grid), np.min(x_grid))

    keep = valid_mask[y_grid.flatten(), x_grid.flatten()].reshape(y_grid.shape)
       
    x_valid = x_grid[keep]
    y_valid = y_grid[keep]

    wcs = WCS(img_fits[0].header, naxis=2)

    # If data is 4D and we extract only 2D, drop the extra dimensions
    if wcs.naxis > 2:
        wcs = wcs.dropaxis(2).dropaxis(2) #wcs.slice((slice(None), slice(None)))
      
    sky_pos_grid = wcs.all_pix2world(x_grid, y_grid, 0)
    sky_pos = wcs.all_pix2world(x_valid, y_valid, 0)

    max_y = np.max(sky_pos[1])
    min_y = np.min(sky_pos[1])

    mask = sky_pos[1] > (max_y - 10)

    points = [(x_grid, y_grid, sky_pos_grid), (x_valid, y_valid, sky_pos)]

    for (xp, yp, sp) in points:

        print('Plotting sky_pos sigma')
        sig_col = np.max(
                (sigmoid(sp[1], max_y-4),
                1-sigmoid(sp[1], min_y+4)),
                axis=0
            ).astype(np.float16)
        print('Finished sigmoid')
    print('Finished')

    sp = sky_pos_grid
    xp = np.array(x_grid).astype(np.int32)
    yp = np.array(y_grid).astype(np.int32)

    sig_col = np.max(
            (sigmoid(sp[1], max_y-4),
            1-sigmoid(sp[1], min_y+4)),
            axis=0
        ).astype(np.float16)

    print(xp.shape, yp.shape, sig_col.shape)

    x_lin = np.arange(img_shape[1], dtype=np.int32)
    y_lin = np.arange(img_shape[0], dtype=np.int32)

    xx, yy = np.meshgrid(x_lin, y_lin)

    print(xx.shape, xx.dtype)

    stripes = 200
    strides = img_shape[1] // stripes

    sp = sky_pos_grid
    xp = np.array(x_grid).astype(np.int32)
    yp = np.array(y_grid).astype(np.int32)

    sig_col = np.max(
            (sigmoid(sp[1], max_y-4),
            1-sigmoid(sp[1], min_y+4)),
            axis=0
        ).astype(np.float16)

    results = []
    i=0
    while i < (img_shape[1]):
        x_lin = np.arange(img_shape[0], dtype=np.int32)
        maxy= min((i+strides),img_shape[1])
        y_lin = np.arange(
                i,maxy,
                dtype=np.int32)
        print(x_lin.max(), y_lin.max())
        yy, xx = np.meshgrid(y_lin, x_lin)

        print('interpolating')
        d = griddata(
                (xp.flatten(), yp.flatten()),
                sig_col.flatten(),
                (yy, xx),
        ).astype(np.float32)
        print(xx.shape, xx.dtype, d.dtype)

        results.append(d)
        if i+strides >= img_shape[1]:
            i = img_shape[1]
        else:
            i+=strides

    dd = np.hstack(results)

    dd[~valid_mask] = np.nan

    print(dd.shape, dd.dtype)

    ddd=1-dd

    return dd, ddd

def create_weightmap(sigmoidweight,rms):
    rms_fits = fits.open(rms)
    valid_mask = np.isfinite(rms_fits[0].data)
    imshape_zeros = np.zeros(valid_mask.shape)
    imshape_zeros[valid_mask] = 1.

    if args.do_mask is True: 
        dist_to_edge = ndimage.distance_transform_edt(imshape_zeros,sampling=[1000,1000])
        edgemask = dist_to_edge <= np.nanmax(dist_to_edge)/5


        lowercut = np.nanquantile(rms_fits[0].data, 0.45)
        uppercut = np.nanquantile(rms_fits[0].data,0.95)
        rms_mask = rms_fits[0].data <= lowercut
        rms_mask2 = rms_fits[0].data >= uppercut

        combined_rms = np.logical_or(rms_mask,rms_mask2)
        combined_mask = np.logical_and(combined_rms,edgemask)
        rms_fits[0].data[combined_mask] = np.nan   
    
    weightmap = sigmoidweight * (1/(rms_fits[0].data**2))

    return weightmap

def interpolate_plane(fits_file, interpolated):
    with fits.open(fits_file) as hdul:
        data = hdul[0].data.copy()
        header = hdul[0].header
        w = WCS(header, naxis=2)
        
        # Generate pixel coordinate grid
        y_indices, x_indices = np.indices(data.shape)
        indexes = np.column_stack([x_indices.ravel(), y_indices.ravel()])

        ra_image, dec_image = w.all_pix2world(indexes[:, 0], indexes[:, 1], 0, ra_dec_order=True)
        c_image = SkyCoord(ra=ra_image, dec=dec_image, unit=(u.degree, u.degree))

        # Identify Galactic plane pixels (to be replaced)
        plane_mask = np.abs(c_image.galactic.b.value) <= 4
        plane_indices = indexes[plane_mask]

        # Identify non-plane (valid) pixels (to be used for interpolation)
        non_plane_mask = np.abs(c_image.galactic.b.value) > 4
        valid_indices = indexes[non_plane_mask]
        valid_values = data[valid_indices[:, 1], valid_indices[:, 0]]

        # Filter out NaN values from valid points
        valid_mask = ~np.isnan(valid_values)
        valid_points = valid_indices[valid_mask]
        valid_values = valid_values[valid_mask]

        interpolated_values = griddata(valid_points, valid_values, plane_indices, method="linear")

        data[plane_indices[:, 1], plane_indices[:, 0]] = interpolated_values
        hdu = fits.PrimaryHDU(data, header=header)
        hdu.writeto(interpolated, overwrite=True) 

    print(f"Interpolation completed and saved to rms_interp.fits")


if __name__ == "__main__":
    parser = ArgumentParser(
        description="create a weighting for a drift night based on a sigmoid weighting, will output the fits image for weighting that should be multiplied by the rms/weights "
    )
    parser.add_argument(
        "infits",
        help="The input image to use for pixels and sky wcs",
    )
    parser.add_argument(
        "rmsfits",
        help="RMS map to use the sigmoid weighting on and produce final weightmap thats input for swarp"
    )
    parser.add_argument(
        "interpolated",
        help="RMS map interpolated to use the sigmoid weighting on and produce final weightmap thats input for swarp"
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
    
    rmsimage = interpolate_plane(args.rmsfits, args.interpolated)
    
    dd, ddd = create_sigweight(args.infits)

    fits.writeto(args.outfits,ddd,overwrite=True)
    
    weightmap = create_weightmap(ddd, args.interpolated)
    fits.writeto(args.outfits, weightmap, overwrite=True)
