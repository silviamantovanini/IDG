#! /usr/bin/env python

from argparse import ArgumentParser


def file_formatter(outname, beam=False, dldm_images=None, diagonal_images=None,
    beam_update_interval=120.,
    dldm_update_interval=120.,
    dldm_window="hann",
    diagonal_update_interval=120.,
    diagonal_window="hann"):
    """
    """

    with open(outname, "w+") as f:
        f.write("aterms = [ ")
        if dldm_images is not None:
            f.write("dldm, ")
        if diagonal_images is not None:
            f.write("diagonal, ")
        if beam:
            f.write("beam ")
        f.write("]\n")

        if beam:
            f.write("beam.update_interval = {}\n".format(beam_update_interval))
        
        if dldm_images is not None:
            f.write("dldm.images = [ ")
            for i, image in enumerate(dldm_images):
                if i < len(dldm_images) - 1:
                    f.write("{}, ".format(image))
                else:
                    f.write("{} ".format(image))
            f.write("]\n")
            f.write("dldm.update_interval = {}\n".format(dldm_update_interval))
            f.write("dldm.window = {}\n".format(dldm_window))

        if diagonal_images is not None:
            f.write("diagonal.images = [ ")
            for i, image in enumerate(diagonal_images):
                if i < len(diagonal_images) - 1:
                    f.write("{}, ".format(image))
                else:
                    f.write("{} ".format(image))
            f.write("]\n")
            f.write("diagonal.update_interval = {}\n".format(diagonal_update_interval))
            f.write("diagonal.window = {}\n".format(diagonal_window))

def main():
    """
    """

    # window options:
    # https://gitlab.com/aroffringa/aocommon/-/blob/master/include/aocommon/windowfunction.h
    windows = ["hann", 
        "tukey", 
        "rectangular", 
        "gaussian", 
        "blackman-harris", 
        "blackman-nutall", 
        "raised-hann"]

    ps = ArgumentParser()
    ps.add_argument("--dldm", nargs="*")
    ps.add_argument("-b", "--beam", action="store_true")
    ps.add_argument("--diagonals", nargs="*")
    ps.add_argument("-o", "--outname", default="aterm.cfg")
    ps.add_argument("-w", "--window", default="hann",
        choices=windows, type=str)


    args = ps.parse_args()

    file_formatter(args.outname,
        beam=args.beam,
        dldm_images=args.dldm,
        diagonal_images=args.diagonals,
        dldm_window=args.window,
        diagonal_window=args.window)


if __name__ == "__main__":
    main()
