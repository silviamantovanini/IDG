#!/usr/bin/env python

__author__ = ("Kat Ross")
__date__ = "13/03/2023"

import csv
from argparse import ArgumentParser


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--mosaicnm",
        type=str,
        dest="mosaicnm",
        help="Name of the mosaic for the catalogue string"

    )
    args = parser.parse_args()

    mosaicnm = args.mosaicnm

    extensions = [
        "69_0000",
        "69_0001",
        "69_0002",
        "69_0003",
        "69_MFS",
        "93_0000",
        "93_0001",
        "93_0002",
        "93_0003",
        "93_MFS",
        "121_0000",
        "121_0001",
        "121_0002",
        "121_0003",
        "121_MFS",
        "145_0000",
        "145_0001",
        "145_0002",
        "145_0003",
        "145_MFS",
        "169_0000",
        "169_0001",
        "169_0002",
        "169_0003",
        "169_MFS"
    ]

    freq_suffixes = [
        "69_0000",
        "69_0001",
        "69_0002",
        "69_0003",
        "69_MFS",
        "93_0000",
        "93_0001",
        "93_0002",
        "93_0003",
        "93_MFS",
        "121_0000",
        "121_0001",
        "121_0002",
        "121_0003",
        "121_MFS",
        "145_0000",
        "145_0001",
        "145_0002",
        "145_0003",
        "145_MFS",
        "169_0000",
        "169_0001",
        "169_0002",
        "169_0003",
        "169_MFS"
    ]

    catalogues = []
    names = []
    images = []
    bkg = []
    rms = []
    psf = []
    suffixes = []
    prefixes = []
    rescaled_cats = []


    for i in range(len(extensions)):
        ext=extensions[i]
        catalogues.append(f"{mosaicnm}_{ext}_ddmod_prior_comp.fits")
        rescaled_cats.append(f"{mosaicnm}_{ext}_ddmod_prior_comp_rescaled.fits")
        # if i in [2, 7, 12, 17, 22]:
        #     suffixes.append(f"_W_{freq_suffixes[i]}MHz")
        # else: 
        suffixes.append(f"_{freq_suffixes[i]}")
        prefixes.append("")
        names.append(f"{mosaicnm}_{ext}")
        images.append(f"{mosaicnm}_{ext}_ddmod.fits")
        bkg.append(f"{mosaicnm}_{ext}_ddmod_bkg.fits")
        rms.append(f"{mosaicnm}_{ext}_ddmod_rms.fits")
        psf.append(f"{mosaicnm}_{ext}_projpsf_psf.fits")

    csv_catalogues_fields = ["#catalogue", "prefix", "suffix"]
    csv_catalogues = [catalogues, prefixes, suffixes]
    csv_cats = zip(*csv_catalogues)
    csv_catalogues_rescaled = [rescaled_cats, prefixes, suffixes]
    csv_cats_rescaled = zip(*csv_catalogues_rescaled)

    csv_image_fields = ["name", "image", "bkg", "rms", "psf"]
    csv_image = [names, images, bkg, rms, psf]    
    csv_ims = zip(*csv_image)

    with open(f"{mosaicnm}_catalogues.csv", "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(csv_catalogues_fields)
        csvwriter.writerows(csv_cats)
    with open(f"{mosaicnm}_images.csv", "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(csv_image_fields)
        csvwriter.writerows(csv_ims)
    with open(f"{mosaicnm}_catalogues_rescaled.csv", "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(csv_catalogues_fields)
        csvwriter.writerows(csv_cats_rescaled)
