#!/usr/bin/env python

# TODO: FREQUENCY BROADCAST

import os
import json

from SSINS import Catalog_Plot as cp, util as ssins_util
from SSINS import SS, INS, MF, plot_lib
from matplotlib import pyplot as plt, cm
import numpy as np
import pylab
from pyuvdata import UVData, UVFlag, utils as uvutils
import sys
import shlex


def get_parser():
    import argparse

    parser = argparse.ArgumentParser(description="Run SSINS on uvfits visibilities.")
    parser.add_argument('--uvfits', default=False, help='uvfits file to flag')
    plot_group = parser.add_argument_group('PLOTTING OPTIONS')
    plot_group.add_argument('--output_prefix', help='Prefix of output plot files', default='')
    plot_group.add_argument('--plot_title', default=None, help="Optional title for the plot")
    plot_group.add_argument('--guard_width', default=0, type=int, help=("Guard width of RFI bands in Hz. " "Half a fine channel width is recommended."))
    plot_group.add_argument('--sel_ants', default=[], nargs='*', type=int, help="antenna indices to select")

    return parser


def main():
    """
    example:

    ```bash
    cp /astro/mwaeor/dev/nfdata/1379177304/prep/birli_1379177304_2s_40kHz.uvfits .
    singularity exec \
        --bind ${PWD} --cleanenv --home /astro/mwaeor/dev/mplhome \
        /pawsey/mwa/singularity/ssins/ssins_latest.sif python \
        /pawsey/mwa/mwaeor/dev/MWAEoR-Pipeline/templates/ssins.py \
        --uvfits=birli_1379177304_2s_40kHz.uvfits \
        --output_prefix=test \
        --plot_title="1379177304" \
        --guard_width=20000 \
        --sel_ants 1 2 3   5 6 7 8 9 10 11 12 13 14 15 \
            16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 \
            32 33 34 35 36 37 38 39    41 42 43 44 45 46 47 \
            48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 \
            64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 \
            80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 \
            96 97 98 99 100 101 102 103 104 105 106 107 108 \
            109 110 111 112 113 114 115 116 117 118 119 120 \
            121 122 123 124 125 126 127 128 129 130 131 132 \
            133 134 135 136 137 138 139 140 141 142 143 144
    """

    parser = get_parser()

    if len(sys.argv) > 1:
        args = parser.parse_args()
    else:
        # is being called directly from nextflow
        args = parser.parse_args(shlex.split("""${args}"""))

    print(vars(args))
    ins_plot_args = {
        "file_ext": "png",
        "title": args.plot_title,
        "extent_time_format": "lst"
    }
    gw = args.guard_width
    shape_dict = {
        "DAB-5A":   [174.160e6 - gw, 175.696e6 + gw],
        "DAB-5B":   [175.872e6 - gw, 177.408e6 + gw],
        "DAB-5C":   [177.584e6 - gw, 179.120e6 + gw],
        "DAB-5D":   [179.296e6 - gw, 180.832e6 + gw],
        "DAB-6A":   [181.168e6 - gw, 182.704e6 + gw],
        "DAB-6B":   [182.880e6 - gw, 184.416e6 + gw],
        "DAB-6C":   [184.592e6 - gw, 186.128e6 + gw],
        "DAB-6D":   [186.304e6 - gw, 187.840e6 + gw],
        "DAB-7A":   [188.160e6 - gw, 189.696e6 + gw],
        "DAB-7B":   [189.872e6 - gw, 191.408e6 + gw],
        "DAB-7C":   [191.584e6 - gw, 193.120e6 + gw],
        "DAB-7D":   [193.296e6 - gw, 194.832e6 + gw],
        "DAB-8A":   [195.168e6 - gw, 196.704e6 + gw],
        "DAB-8B":   [196.880e6 - gw, 198.416e6 + gw],
        "DAB-8C":   [198.592e6 - gw, 200.128e6 + gw],
        "DAB-8D":   [200.304e6 - gw, 201.840e6 + gw],
        "DAB-9A":   [202.160e6 - gw, 203.696e6 + gw],
        "DAB-9B":   [203.872e6 - gw, 205.408e6 + gw],
        "DAB-9C":   [205.584e6 - gw, 207.120e6 + gw],
        "DAB-9D":   [207.296e6 - gw, 208.832e6 + gw],
        "DAB-10A":  [209.168e6 - gw, 210.704e6 + gw],
        "DAB-10B":  [210.880e6 - gw, 212.416e6 + gw],
        "DAB-10C":  [212.592e6 - gw, 214.128e6 + gw],
        "DAB-10D":  [214.304e6 - gw, 215.840e6 + gw],
        "DAB-11A":  [216.160e6 - gw, 217.696e6 + gw],
        "DAB-11B":  [217.872e6 - gw, 219.408e6 + gw],
        "DAB-11C":  [219.584e6 - gw, 221.120e6 + gw],
        "DAB-11D":  [221.296e6 - gw, 222.832e6 + gw],
        "DAB-12A":  [223.168e6 - gw, 224.704e6 + gw],
        "DAB-12B":  [224.880e6 - gw, 226.416e6 + gw],
        "DAB-12C":  [226.592e6 - gw, 228.128e6 + gw],
        "DAB-12D":  [228.304e6 - gw, 229.840e6 + gw],
        # packet loss
        "PL-C":     [177.000e6 - gw, 187.000e6 + gw], # centre

    }
    sig_thresh = {shape: 5 for shape in shape_dict}
    sig_thresh['narrow'] = 7
    sig_thresh['streak'] = 8

    ss = SS()
    ss.read(args.uvfits, read_data=False, file_type="ms")

    # discaring the first and last tiemstamp
    # times = np.unique(ss.time_array)[1:-1]
    times = np.unique(ss.time_array)
    print(np.sort(np.unique(ss.ant_1_array)))
    kwargs = {
        "times": times,
    }
    if args.sel_ants:
        kwargs["antenna_nums"] = args.sel_ants
    ss.read(args.uvfits, read_data=True, diff=True, file_type="ms", **kwargs)
    ss.apply_flags(flag_choice='original')

    # cp.VDH_plot(ss, 'ssins_vdh', file_ext='png',
    #     pre_flag=True, post_flag=True, pre_model=False, post_model=False,
    #     post_label='Post-Flag Data', pre_label='Pre-Flag Data',
    #     legend=True)

    # RFI in autos
    ins_autos = INS(ss, spectrum_type="auto")
    cp.INS_plot(ins_autos, f'{args.output_prefix}autos', **ins_plot_args)

    # RFI in crosses
    ins_cross = INS(ss, spectrum_type='cross')
    cp.INS_plot(ins_cross, f'{args.output_prefix}cross', **ins_plot_args)

    mf = MF(ins_cross.freq_array, sig_thresh, shape_dict=shape_dict, streak=True, narrow=True)
    ins_cross.metric_array[ins_cross.metric_array == 0] = np.ma.masked
    ins_cross.metric_ms = ins_cross.mean_subtract()
    ins_cross.sig_array = np.ma.copy(ins_cross.metric_ms)
    mf.apply_match_test(ins_cross)

    cp.INS_plot(ins_cross, f'{args.output_prefix}flagged', **ins_plot_args)
    occ_dict = ssins_util.calc_occ(ins_cross, mf, 0)
    with open(f'{args.output_prefix}ssins_occ.json', "w") as json_file:
        json.dump(occ_dict, json_file, indent=4)

    # with open(f'{args.output_prefix}ssins_events.json', "w") as events_file:
    #     events_obj = [
    #         {
    #             'time_bounds': [int(event[0].start), int(event[0].stop)],
    #             'freq_bounds': [int(event[1].start), int(event[1].stop)],
    #             'shape': event[2],
    #             'sig': event[3] if event[3] is None else float(event[3])
    #         } for event in ins_cross.match_events
    #     ]
    #     json.dump(events_obj, events_file, indent=4)

    ins_cross.write(f'{args.output_prefix}', output_type='mask', clobber=True)

    # flags = ins_cross.mask_to_flags()
    # uvd = UVData()
    # uvd.read(args.uvfits, times=times)
    # uvf = UVFlag(uvd, waterfall=True, mode='flag')
    # uvf = ins_cross.flag_uvf(uvf)
    # uvutils.apply_uvflag(uvd, uvf)


if __name__ == '__main__':
    main()
