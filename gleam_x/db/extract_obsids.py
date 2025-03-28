#!/usr/bin/env python

import numpy as np
import subprocess
import sys
from astropy.io import fits
import re

def extract_obsids_from_fits(fits_file):
    # Extract observation IDs from HISTORY entries in a FITS header.
    with fits.open(fits_file) as hdul:
        header = hdul[0].header

        # Convert to strings to prevent TypeErrors
        history_lines = [str(header[key]) for key in header if key.startswith('HISTORY')]

    # Regex to match a 10-digit number followed by ".ms"
    obsid_pattern = re.compile(r'\b(\d{10})\.ms\b')

    obsids = set()

    for line in history_lines:
        matches = obsid_pattern.findall(line)  # Extract valid ObsIDs
        obsids.update(matches)

    return sorted(map(int, obsids))
    
    
def save_obsids_to_file(obsids, output_file):
    # Save the extracted observation IDs to a text file.
    with open(output_file, 'w') as f:
        for obsid in obsids:
            f.write(f"{obsid},\n")
    print(f"Observation IDs saved to {output_file}")
    
    
input_fits = sys.argv[1]
output_file = sys.argv[2]

# Extract observation IDs from FITS header
obsids = extract_obsids_from_fits(input_fits)

# Save to file
save_obsids_to_file(obsids, output_file)
