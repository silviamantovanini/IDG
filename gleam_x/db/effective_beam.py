#!/usr/bin/env python

import numpy as np
import sys
from astropy.io import fits
import os

def average_observation_beams(obsid_list_file, subchan, output_fits):
    # Averages beam pairs (XX, YY) per observation, then averages across all observations.
    
    # Read observation IDs from file
    with open(obsid_list_file, 'r') as f:
        obsids = [line.strip().split(',')[0] for line in f if line.strip()]
    
    if not obsids:
        print("Error: No observations found in the list.")
        sys.exit(1)
    
    all_beam_data = []

    for obs in obsids:
        xx_fits = f"{obs}-XX-{subchan}-beam.fits"
        yy_fits = f"{obs}-YY-{subchan}-beam.fits"

        if not os.path.exists(xx_fits) or not os.path.exists(yy_fits):
            print(f"Warning: Missing files for {obs} (Skipping)")
            continue

        try:
            with fits.open(xx_fits) as hdu_xx, fits.open(yy_fits) as hdu_yy:
                beam_xx = hdu_xx[0].data
                beam_yy = hdu_yy[0].data

                # Compute per-observation average beam
                beam = (beam_xx + beam_yy) / 2.0
                all_beam_data.append(beam)
        
        except Exception as e:
            print(f"Error processing {obs}: {e}")
            continue
    
    if not all_beam_data:
        print("Error: No valid beam data available for averaging.")
        sys.exit(1)
    
    # Convert to numpy array and compute final averaged beam
    stacked_beams = np.array(all_beam_data)
    final_averaged_beam = np.nanmean(stacked_beams, axis=0)

    # Save output to new FITS file
    with fits.open(xx_fits) as hdu_template:
        hdu_template[0].data = final_averaged_beam
        hdu_template.writeto(output_fits, overwrite=True)

    print(f"Final averaged beam saved to {output_fits}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python effective_beam.py <obsid_list.txt> <subchan> <output_beam.fits>")
        sys.exit(1)

    obsid_list_file = sys.argv[1]
    subchan = sys.argv[2]
    output_fits = sys.argv[3]

    average_observation_beams(obsid_list_file, subchan, output_fits)
