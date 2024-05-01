#! /usr/bin/env python

import numpy as np

from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS
from argparse import ArgumentParser

import logging
logging.basicConfig(format="%(levelname)s (%(module)s): %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def radec_to_lm(ra, dec, ra0, dec0):
    """Convert RA,DEC to l,m."""

    l = np.cos(dec)*np.sin(ra-ra0)
    m = np.sin(dec)*np.cos(dec0) - np.cos(dec)*np.sin(dec0)*np.cos(ra-ra0)

    return l, m

def downsample(image, outsize, outname, fill_value=np.nan):
    """
    """

    with fits.open(image) as f:

        w = WCS(f[0].header).celestial
        fdata = np.squeeze(f[0].data).copy()
        x, y = np.indices(np.squeeze(f[0].data).shape)

        # r, d = w.all_pix2world(x, y, 0)

        stridex = f[0].header["NAXIS1"] // outsize
        # stridey = f[0].header["NAXIS2"] // outsize
        # logger.debug("stridex = {}".format(stridex))

        mid_stridex = stridex // 2
        mid_r = f[0].header["NAXIS1"] % outsize
        logger.debug("stridex: {}, mid_r: {}".format(stridex, mid_r))
        # mid_r = 0
        # mid_stridey = stridey // 2

        if "CD1_1" in f[0].header.keys():
            cdx = f[0].header["CD1_1"]
            cdy = f[0].header["CD2_2"]
        elif "CDELT1" in f[0].header.keys():
            cdx = f[0].header["CDELT1"]
            cdy = f[0].header["CDELT2"]
        else:
            raise ValueError("No pixel scale information found!")

        cellx = stridex * cdx  # Negative!
        celly = stridex * cdy

        logger.debug("cell: {}".format(celly))

        out_arr = np.full((outsize, outsize), fill_value)

        X, Y = [], []
        I, J = [], []
        ra, dec = [], []

        nx = 0
        for i in range(mid_stridex, f[0].header["NAXIS1"]-stridex-mid_r, stridex):
            ny = 0
            for j in range(mid_stridex, f[0].header["NAXIS1"]-stridex-mid_r, stridex):

                # logger.debug("{}  , {}".format(nx, ny))

                X.append(nx)
                Y.append(ny)
                I.append(i)
                J.append(j)

                # r, d = w.all_pix2world(i, j, 0)

                # ra.append(r)
                # dec.append(d)

                # Get average z:
                z_avg = np.nanmean(fdata[i-mid_stridex:i+mid_stridex, j-mid_stridex:j+mid_stridex])
# 
                out_arr[nx, ny] = z_avg

                ny += 1
            nx += 1

    ra, dec = w.all_pix2world(np.asarray(I), np.asarray(J), 0)

    # Initialise output FITS image:
    hdu = fits.PrimaryHDU()
    hdu.data = out_arr

    hdu.header["CTYPE1"] = "RA---SIN"
    hdu.header["CTYPE2"] = "DEC--SIN"
    hdu.header["CRVAL1"] = ra[len(X)//2]
    hdu.header["CRVAL2"] = dec[len(X)//2]
    hdu.header["CRPIX1"] = X[len(X)//2]
    hdu.header["CRPIX2"] = Y[len(X)//2]
    hdu.header["CDELT1"] = cellx
    hdu.header["CDELT2"] = celly 

    hdu.writeto(outname, overwrite=True)

    # hdu.close()     
    return outname

# default 1 antenna assumes all antennas are the same.
# nope new default has to be equal to number of antennas.
def create_diag_file(gains, freq, mjdtime, outname, scanlength, bandwidth, 
    antennas=128, 
    pad=0,
    abs_pad=None,
    ones=False):
    """
    Padding should be used.
    """


    gains2d = np.squeeze(gains[0].data)
    gains2d[:] = np.nanmedian(gains2d)
    gains2d[~np.isfinite(gains2d)] = 1.
    gains2d[gains2d <= 0] = 1.

    # for now only take single value - what would position-dependent gains even be?

    gainshdr = gains[0].header

    if abs_pad is None:
        pad_pixels = int(gainshdr["NAXIS1"]*pad)
    else:
        pad_pixels = abs_pad
    # need to be even for halving
    if pad_pixels%2 != 0:
        pad_pixels += 1

    new_shape = (gains2d.shape[0]+pad_pixels, gains2d.shape[1]+pad_pixels)
    # no complex numbers in fits image hdus?
    data = np.full((1, 1, antennas, 4, new_shape[0], new_shape[1]), 1.)

    for i in range(antennas): 
        if not ones:
            data[0, 0, i, 0, 
                int(pad_pixels//2):new_shape[0]-int(pad_pixels//2), 
                int(pad_pixels//2):new_shape[0]-int(pad_pixels//2)] = gains2d
            data[0, 0, i, 2, 
                int(pad_pixels//2):new_shape[0]-int(pad_pixels//2), 
                int(pad_pixels//2):new_shape[0]-int(pad_pixels//2)] = gains2d
        data[0, 0, i, 1, :, :] = 0.
        data[0, 0, i, 3, :, :] = 0.

    hdu = fits.PrimaryHDU()
    hdu.data = data

    for i in ["1", "2"]:
        hdu.header["CTYPE"+i] = gainshdr["CTYPE"+i]
        hdu.header["CRVAL"+i] = gainshdr["CRVAL"+i]
        hdu.header["CRPIX"+i] = gainshdr["CRPIX"+i]+int(pad_pixels//2)
        hdu.header["CDELT"+i] = gainshdr["CDELT"+i]

    hdu.header["CTYPE3"] = "MATRIX"
    # hdu.header["CRPIX3"] = 1.
    # hdu.header["CRVAL3"] = 0.

    hdu.header["CTYPE4"] = "ANTENNA"
    hdu.header["CRPIX4"] = 1.
    hdu.header["CRVAL4"] = 0.

    hdu.header["CTYPE5"] = "FREQ"
    hdu.header["CRPIX5"] = 1.
    hdu.header["CRVAL5"] = freq
    hdu.header["CDELT5"] = bandwidth
    hdu.header["CUNIT5"] = "Hz"

    hdu.header["CTYPE6"] = "TIME"
    hdu.header["CRPIX6"] = 1.
    hdu.header["CRVAL6"] = mjdtime
    hdu.header["CDELT6"] = scanlength

    hdu.writeto(outname, overwrite=True)

def create_dldm_file(dx, dy, cdelt, freq, mjdtime, outname, scanlength, bandwidth, 
    antennas=128,
    pad=0.2, 
    abs_pad=None,
    zeroes=False,
    fill_x=None,
    fill_y=None):
    """
    """

    # should this be in radians? I think TEC stuff normally is? based on EveryBeam dldm*.cc it seems like it is degrees
    dl = -np.radians(np.squeeze(dx[0].data)*cdelt)
    dm = np.radians(np.squeeze(dy[0].data)*cdelt)
    gainshdr = dx[0].header

    dl[~np.isfinite(dl)] = 0.
    dm[~np.isfinite(dm)] = 0.

    if abs_pad is None:
        pad_pixels = int(gainshdr["NAXIS1"]*pad)
    else:
        pad_pixels = abs_pad
    print("padding pixels: {}".format(pad_pixels))
    # need to be even for halving
    if pad_pixels%2 != 0:
        pad_pixels += 1

    new_shape = (dl.shape[0]+pad_pixels, dl.shape[1]+pad_pixels)
    data = np.full((1, 1, antennas, 2, new_shape[0], new_shape[1]), 0.)
    data_test = np.full(new_shape, 0.)

    if fill_x is not None:
        fill_x = -(np.radians(fill_x*cdelt))
    if fill_y is not None:
        fill_y = np.radians(fill_y*cdelt)

    if not zeroes:
        for i in range(antennas):
            if fill_x is not None:
                data[0, 0, i, 0, 
                    int(pad_pixels//2):new_shape[0]-int(pad_pixels//2), 
                    int(pad_pixels//2):new_shape[0]-int(pad_pixels//2)] = fill_x
            else:
                data[0, 0, i, 0, 
                    int(pad_pixels//2):new_shape[0]-int(pad_pixels//2), 
                    int(pad_pixels//2):new_shape[0]-int(pad_pixels//2)] = dl
            if fill_y is not None:
                data[0, 0, i, 1, 
                    int(pad_pixels//2):new_shape[0]-int(pad_pixels//2), 
                    int(pad_pixels//2):new_shape[0]-int(pad_pixels//2)] = fill_y
            else:
                data[0, 0, i, 1, 
                    int(pad_pixels//2):new_shape[0]-int(pad_pixels//2), 
                    int(pad_pixels//2):new_shape[0]-int(pad_pixels//2)] = dm

    hdu = fits.PrimaryHDU()
    hdu.data = data

    for i in ["1", "2"]:
        hdu.header["CTYPE"+i] = gainshdr["CTYPE"+i]
        hdu.header["CRVAL"+i] = gainshdr["CRVAL"+i]
        hdu.header["CRPIX"+i] = gainshdr["CRPIX"+i]+int(pad_pixels//2)
        hdu.header["CDELT"+i] = gainshdr["CDELT"+i]

    hdu.header["CTYPE3"] = "MATRIX"
    hdu.header["CRPIX3"] = 1.
    hdu.header["CRVAL3"] = 0.

    hdu.header["CTYPE4"] = "ANTENNA"
    hdu.header["CRPIX4"] = 1.
    hdu.header["CRVAL4"] = 0.

    hdu.header["CTYPE5"] = "FREQ"
    hdu.header["CRPIX5"] = 1.
    hdu.header["CRVAL5"] = freq
    hdu.header["CDELT5"] = bandwidth
    hdu.header["CUNIT5"] = "Hz"

    hdu.header["CTYPE6"] = "TIME"
    hdu.header["CRPIX6"] = 1.
    hdu.header["CRVAL6"] = mjdtime
    hdu.header["CDELT6"] = scanlength

    hdu.writeto(outname, overwrite=True)

    dx.close()
    dy.close()


def main():
    """
    """

    # TODO: change `gpstime` variable to `mjdtime`

    ps = ArgumentParser()

    ps.add_argument("-d", "--diagonal", type=str, default=None, 
                    help="Name of the diagonal gains 2-d FITS screen (e.g. output from flux_warp). TODO: allow separate XX,YY corrections.")
    ps.add_argument("-a", "--antennas", type=int, default=128,
                    help="Number of antennas. Default 127.")
    ps.add_argument("-x", "--dx", type=str, default=None,
                    help="Name of the dx positional offsets 2-d FITS screen (e.g. output from fits_warp.py).")
    ps.add_argument("-y", "--dy", type=str, default=None,
                    help="Name of the dy positional offsets 2-d FITS screen (e.g. output from fits_warp.py).")
    ps.add_argument("-t", "--time", type=float, default=None,
                    help="MJD time in seconds if not providing a metafits file.")
    ps.add_argument("-f", "--frequency", type=float, default=None,
                    help="Reference frequency in Hz for observation if not providing a metafits file.")
    ps.add_argument("-l", "--scanlength", type=float, default=None,
                    help="Scan length in seconds if not providing a metafits file.")
    ps.add_argument("-b", "--bandwidth", type=float, default=None,
                    help="Bandwidth of observation in Hz if not providing a metafits file.")
    ps.add_argument("-o", "--outbase", default="aterm", type=str,
                    help="Base output name. Diagonal gains files will be named outbase_diag.fits, and dl,dm files will be outbase_dldm.fits.")
    ps.add_argument("-m", "--metafits", type=str, default=None,
                    help="Name of metafits file for MWA observation. Required unless all other parameters are specified.")
    ps.add_argument("--dfd", default=1024, type=float,
                    help="Downsampled diagonal gain image size on one side [default 1024].")
    ps.add_argument("--pad", default=0.2, type=float,
                    help="Padding fraction of image for diagonal gains.")
    ps.add_argument("--dflm", default=1024, type=float,
                    help="Downsampled dl,dm image sizes on one side [default 1024].")
    ps.add_argument("--ones", action="store_true",
                    help="Make diagonal a-term map with only ones.")
    ps.add_argument("--zeroes", "--zeros", dest="zeroes", action="store_true",
                    help="Make dl,dm a-term map with only zeroes.")
    ps.add_argument("--fill_x", default=None, type=float,
                    help="Fill dx value for dl - this is used instead of supplied screen.")
    ps.add_argument("--fill_y", default=None, type=float,
                    help="Fill dy value for dm - this is used instead of the supplied screen.")
    ps.add_argument("--abs-pad", "--abs_pad", dest="abs_pad", type=float,
                    default=None)

    args = ps.parse_args()

    args.dfd = int(args.dfd)
    args.dflm = int(args.dflm)
    if args.abs_pad is not None:
        args.abs_pad = int(args.abs_pad)
        
    
    

    if (args.time is None or \
        args.frequency is None or \
        args.bandwidth is None or \
        args.scanlength is None) \
            and args.metafits is not None:

            mhdr = fits.getheader(args.metafits)
            args.time = Time(mhdr["DATE-OBS"], format="isot", scale="utc")
            args.time = Time(args.time, format="mjd").value*86400.  # in seconds
            args.frequency = mhdr["FREQCENT"]*1e6
            args.scanlength = fits.getheader(args.metafits)["EXPOSURE"]
            args.bandwidth = fits.getheader(args.metafits)["BANDWDTH"]*1e6

    elif (args.time is None or \
          args.frequency is None or \
          args.bandwidth is None or \
          args.scanlength is None):
        raise RuntimeError("If no metafits file is supplied time, frequency, bandwidth, AND scanlength must be provided.")

    if args.diagonal is not None: 

        outname = args.outbase + "_diag.fits"

        if args.dfd > 0:
            args.diagonal = downsample(image=args.diagonal,
                outsize=args.dfd,
                outname=args.diagonal.replace(".fits", "_{}.fits".format(args.dfd)),
                fill_value=1.
            )

        with fits.open(args.diagonal) as gains:
            create_diag_file(gains=gains,
                freq=args.frequency,
                mjdtime=args.time,
                outname=outname,
                scanlength=args.scanlength,
                bandwidth=args.bandwidth,
                pad=args.pad,
                abs_pad=args.abs_pad,
                ones=args.ones,
                antennas=args.antennas
            )

    if args.dx is not None and args.dy is not None:
        outname = args.outbase + "_dldm.fits"

        cdelt = fits.getheader(args.dx)["CDELT2"]

        if args.dflm > 0:
            args.dx = downsample(image=args.dx,
                outsize=args.dflm,
                outname=args.dx.replace(".fits", "_{}.fits".format(args.dflm)),
                fill_value=0.)
        
            args.dy = downsample(image=args.dy,
                outsize=args.dflm,
                outname=args.dy.replace(".fits", "_{}.fits".format(args.dflm)),
                fill_value=0.)

        create_dldm_file(
            dx=fits.open(args.dx),
            dy=fits.open(args.dy),
            cdelt=cdelt,
            freq=args.frequency,
            mjdtime=args.time,
            outname=outname,
            scanlength=args.scanlength,
            bandwidth=args.bandwidth,
            pad=args.pad,
            abs_pad=args.abs_pad,
            zeroes=args.zeroes,
            antennas=args.antennas
        )

if __name__ == "__main__":
    main()
