#!/usr/bin/env python 

import numpy as np
import sys
from tqdm import trange

from datetime import datetime
from casacore import tables
from matplotlib import pyplot as plt, cm
from casacore.tables import *

plt.rcParams.update({
    "font.size": 10,
    "font.sans-serif": ["Helvetica"]})

cm = 1/2.54

# ---------------------------------------------------------------------------- #
# Simple RFI flagging on MWA MeasurementSets.
# ---------------------------------------------------------------------------- #

def get_values(pols):
	# pols = data[:, channels, 0:4] or pols = data[:, 0:4]
	return 0.5*np.abs(pols[..., 0] + pols[..., 3])
	# return pols

def auto_clip(msname, clip=3, width=10, column="DATA", mode="median",
	writeout=None,
	scale_freq=False,
	fit_bandpass=0,
	use_single_std=False):
	"""Simple but quicker autoclipping routine."""

	t1 = datetime.now()

	if isinstance(msname, str):
		MeasurementSet = tables.table(msname, readonly=True, ack=False)
	else:
		MeasurementSet = msname

	filtered = tables.taql("select * from $msname where not FLAG_ROW and ANTENNA1 <> ANTENNA2")
	freqs = filtered.SPECTRAL_WINDOW.getcell("CHAN_FREQ", 0)
	midfreq = np.array([(min(freqs) + max(freqs)) / 2])
	if scale_freq:
		fratio = (freqs/midfreq)**2
	else:
		fratio = np.full((len(freqs),), 1.)

	data = filtered.getcol(column)
	flags = filtered.getcol("FLAG")
	data[flags] = np.nan
	nchans = data.shape[1]
	print("Total {} channels in {}".format(nchans, MeasurementSet.name()))
	all_channels = np.arange(0, nchans)

	#print(data[flags].shape)
	#print(data.shape[0]*data.shape[1]*data.shape[2])
	print(" - Flagged = %.1f%%" %((100*data[flags].shape[0])/(data.shape[0]*data.shape[1]*data.shape[2])))

	print("")
	print("Calculating statistics...")
	print("Calculating {} channel amplitudes...".format(mode))
	if mode.lower() == "median":
		nanavg = np.nanmedian
	elif mode.lower() == "mean":
		nanavg = np.nanmean
	else:
		print("Mode is being set to \"median\"")
		nanavg = np.nanmedian

	flag_channels = []

	med = None
	std = None

	original_channels_medians = np.full((nchans,), 0.)
	channels_stds = np.full((nchans,), 0.)
	window_medians = np.full((nchans,), 0.)
	window_stds = np.full((nchans,), 0.)
	
	pbar = trange(nchans)
	for i in pbar:
		# precalculate medians before window calculations
		value = get_values(pols=data[:, i, :])
		med = nanavg(value)
		std = np.nanstd(value)
		pbar.set_description("channel {} med {:.2f}, std {:.2f}".format(
			i, med, std
		))

		original_channels_medians[i] = med
		channels_stds[i] = std

	# print(channels_medians)
	# print(all_channels
	if fit_bandpass > 0:
		print("Fitting {} deg bandpass".format(fit_bandpass))
		fit = np.polynomial.Polynomial.fit(
			all_channels[np.isfinite(original_channels_medians)],
			original_channels_medians[np.isfinite(original_channels_medians)],
			deg=fit_bandpass,
			w=1./channels_stds[np.isfinite(original_channels_medians)],
			full=False
		)
		print(fit.convert().coef)
		bandpass = fit(all_channels)
	else:
		bandpass = np.full((len(original_channels_medians),), 1.)

	channels_medians = original_channels_medians / bandpass

	# print("Getting medians")
	# channels_medians = nanavg(get_values(pols=data), axis=0)
	# channels_stds = np.nanstd(get_values(pols=data), axis=0)
	# print("Medians got")

	# channels_medians *= fratio
	# window_medians *= fratio

	med = nanavg(channels_medians)
	std = np.nanstd(channels_medians)
	bulk_std = np.nanstd(channels_medians)
	print("overall std: {}".format(bulk_std))

	pbar = trange(nchans)
	bad_channels_medians = []
	threshold_up = []
	threshold_down = []
	for i in pbar:

		pbar.set_description("channel {}".format(i))

		if width*2+1 < nchans:
			window_min = np.max([0, i-width])
			window_max = np.min([nchans, i+width+1])

			# values = get_values(
			# 	pols=data[:, window_min:window_max, :],
			# )

			std = np.nanstd(channels_medians[window_min:window_max])
			# std = np.nanstd(values)
			# med = nanavg(values) * np.mean(fratio[window_min:window_max])
			med = nanavg(channels_medians[window_min:window_max])

		window_medians[i] = med
		window_stds[i] = std

		if use_single_std:
			std_i = bulk_std
		else:
			std_i = std
		threshold_up.append(clip*std_i + abs(med))
		threshold_down.append(abs(med) - clip*std_i)

		if abs(channels_medians[i]) > (clip*std_i) + abs(med) or \
			abs(channels_medians[i]) < abs(med) - (clip*std_i):
			flag_channels.append(i)
			bad_channels_medians.append(channels_medians[i])

	print("")
	print("Found {} channels to flag in {} hours".format(
		len(flag_channels),
		datetime.now()-t1)
	)

	#Making a plot
	#Plotting the median of the visibilities per channel.

	fig = plt.figure(figsize=(20*cm, 15*cm))
	ax = fig.add_subplot(111)

	ax.fill_between(x=all_channels, y1=threshold_down, y2=threshold_up, alpha=0.3, color="grey")
	ax.scatter(all_channels, channels_medians, marker="o", color="darkgreen")
	ax.scatter(flag_channels, bad_channels_medians, marker="o", color="red")
	#ax.axhline(med, linestyle='--', color='grey')

	ax.set_xlim([0, 768])
	ax.set_ylabel("Median")
	ax.set_xlabel("Channel")
	ax.set_title(f"Channels to be flagged:\n{flag_channels}\nData already flagged: %.1f%%" %((100*data[flags].shape[0])/(data.shape[0]*data.shape[1]*data.shape[2])))
	ax.title.set_color('darkred')

	outname = f"{args.msname}_median_per_channel.png"
	fig.savefig(outname, bbox_inches="tight")

	if writeout is not None:
		with open(writeout, "w+") as f:
			f.write("channel,freq,fratio,bandpass,original_median,median,std,window_median,window_std,flag\n")
			for i in all_channels:
				if i in flag_channels:
					f.write("{},{},{},{},{},{},{},{},{},1\n".format(
						i, 
						freqs[i],
						fratio[i],
						bandpass[i],
						original_channels_medians[i],
						channels_medians[i], 
						channels_stds[i],
						window_medians[i],
						window_stds[i]
					))
				else:
					f.write("{},{},{},{},{},{},{},{},{},0\n".format(
						i, 
						freqs[i],
						fratio[i],
						bandpass[i],
						original_channels_medians[i],
						channels_medians[i], 
						channels_stds[i],
						window_medians[i],
						window_stds[i]
					))

	

	return flag_channels


def auto_clip_(msname, clip=3, width=10, column="DATA", mode="median",
	noprogress=False):
	"""Simple autoclipping routine. 

	- For all channels, calculate median amplitude over baseline/times.- 
	"""

	t1 = datetime.now()

	if isinstance(msname, str):
		MeasurementSet = tables.table(msname, readonly=False, ack=False)
	else:
		MeasurementSet = msname

	row0 = MeasurementSet.row().get(0)
	nchans = row0["DATA"].shape[0]
	nrows = MeasurementSet.nrows()
	print("Total {} channels in {}".format(nchans, MeasurementSet.name()))

	all_channels = np.array(range(0, nchans))
	flag_channels = []

	channel_vis_amp = {}
	channel_vis_med = {}
	for c in all_channels:
		channel_vis_amp[c] = []
		channel_vis_med[c] = np.nan 

	print("Reading and arranging MeasurementSet...")

	pbar = trange(nrows)
	for i in pbar:

		# if i%f == 0:
			# sys.stdout.write("{0:3.0f}%...".format(100*i/nrows))
			# sys.stdout.flush()
		if not noprogress:
			pbar.set_description("Processing row {}".format(i))

		row = MeasurementSet.row().get(i)
		data = row[column].real
		flags = row["FLAG"]
		data[np.where(flags == True)] = np.nan

		abs_amp = 0.5*abs(data[:, 0] + data[:, 3])
		for c in all_channels:
			channel_vis_amp[c].append(abs_amp[c])

	print("")
	print("Calculating statistics...")
	print("Calculating {} channel amplitudes...".format(mode))
	if mode.lower() == "median":
		nanavg = np.nanmedian
	elif mode.lower() == "mean":
		nanavg = np.nanmean
	else:
		print("Mode is being set to \"median\"")
		nanavg = np.nanmedian

	for c in all_channels:
		channel_vis_med[c] = np.nanmax(channel_vis_amp[c])

	print("Sliding window over channels...")

	for c in all_channels:
		if c > width and c < nchans-width:

			window = [c-w for w in range(1, width+1)] + \
					 [c+w for w in range(1, width+1)]

			meds = []
			for w in window:
				if w not in flag_channels:
					meds.append(channel_vis_med[w])
			window_med = nanavg(np.asarray(meds))
			# std = np.nanstd(np.asarray(meds))
			if abs(channel_vis_med[c]) > clip*abs(window_med):
				flag_channels.append(c)

	print("")
	print("Found {} channels to flag in {} hours".format(len(flag_channels),
													     datetime.now()-t1)
		  )


	return flag_channels



def apply_flags(msname, channels, pad=None, write=True, noprogress=False):
	"""Flag channels in `channel`s.

	All instrumental polarizations are flagged for all time intervals/baselines.
	
	"""

	t1 = datetime.now()
	
	if isinstance(msname, str):
		MeasurementSet = tables.table(msname, readonly=False, ack=False)
	else:
		MeasurementSet = msname

	try:
		row0 = MeasurementSet.row().get(0)
		nchans = row0["DATA"].shape[0]
		nrows = MeasurementSet.nrows()
		print("Total {} channels in {}".format(nchans, msname))

		if pad is not None:
			for c in channels[:]:
				if c-1 >= 0 and c-1 not in channels:
					channels.append(c-1)
				if c+1 < nchans and c+1 not in channels:
					channels.append(c+1)

		channels = sorted(channels)

		print("Flagging channels: {}".format([i+1 for i in channels]))

		pbar = trange(nrows)
		for i in pbar:

			if not noprogress:
				pbar.set_description("Applying flags to row {}".format(i))

			row = MeasurementSet.row().get(i)

			flags = row["FLAG"]
			for c in channels:
				flags[c, :] = True
			row["FLAG"] = flags

			MeasurementSet.row().put(i, row)


		print("")
		print("Flushing changes to {}".format(msname))
		MeasurementSet.close()
		print("FLags written in {}".format(datetime.now()-t1))

	except:
		raise
	finally:
		if write:
			MeasurementSet.close()


def channels_to_indices(channels):
	"""Given a string representation of channels, return 0-indexed indices.

	Formats follow:
	1,2,3,4,...
	1,3,5,7,8,..
	1-5
	1-5,7,8,55-66
	1

	"""

	chans = str(channels)
	if "-" not in chans and "," not in chans:
		return int(chans)-1

	elif "," in chans:

		all_channels = []
		split_chans = chans.split(",")

		for chan in split_chans:
			if "-" in chan:
				start, end = chan.split("-")
				all_channels += range(int(start)-1, int(end))
			else:
				all_channels.append(int(chan)-1)

		return all_channels

	else:

		start, end = chans.split("-")
		return range(int(start)-1, int(end))



if __name__ == "__main__":
	"""For command-line use."""

	import argparse
	ps = argparse.ArgumentParser(description="Flag channels in a MeasurementSet.")

	help_ = {"msname": "MeasurementSet.",
			 "channels": "Channels to flag. 1-indexed. Acceptable formats are "
		 				 "e.g.: 1,2,5,8,... | 1-5 | 1-5,7,9,55-66 | 1.", 
		 	 "pad": "Extended flags this amount either side of the selected "
		 	 		"channels. Only used when applying flags. [Default None]",
		 	 "sigma": "Clip level for auto-flagging. For every channel, std is "
		 	 		  "is computed for the median values of 2*window+1 channels."
		 	 		  " If the median amplitude of the central channel is more "
		 	 		  "than clip*std different from the median of the window "
		 	 		  "medians the central channel is flagged. [Default 3]",
		 	 "window": "The actual window is -window to +window on either side"
		 	 		   " of a given channel. [Default 10 (21 channels)]",
		 	 "auto": "Switch for a simple auto-flagging routine based on "
		 	 		 "median-stddev clipping.",
		 	 "data_column": "Switch for using the DATA column. By default "
		 	 				"the CORRECTED_DATA column is used if it exists.",
			 "low": "Switch to use a much slower low memory mode - legacy option.",
			 "freq_scale": "Switch to scale channel medians by frequency to flatten "
			               "frequency-dependent changes across the bandpass.",
			 "write": "Switch to write out csv file of channel medians and flags.",
			 "std": "Switch to use overall stddev instead of window stddev.",
			 "noapply": "Switch to disable application of flags. It is suggested to use"
			            " e.g. CASA flagdata to apply flags.",
			 "function": "Use mean or median calculation. [Default 'median']",
			 "bandpass": "Degree polynomial to fit to the bandpass before removal."
			  		     " If < 1, not bandpass removal is done. [Default 0]"
	}

	ps.add_argument("msname", 
		type=str, 
		help=help_["msname"]
	)
	
	ps.add_argument("-c", "--channels", 
		type=str, 
		help=help_["channels"]
	)
	
	ps.add_argument("-p", "--pad", 
		type=int, 
		default=None, 
		help=help_["pad"]
	)
	
	ps.add_argument("-s", "--sigma", "--clip", 
		dest="clip",
		type=float, 
		default=3,
		help=help_["sigma"]
	)

	ps.add_argument("-w", "--window", 
		type=int, 
		default=10, 
		help=help_["window"]
	)

	ps.add_argument("-a", "--auto", 
		action="store_true", 
		help=help_["auto"]
	)

	ps.add_argument("-d", "--data_column", 
		default=None, 
		help=help_["data_column"]
	)

	ps.add_argument("-f", "--function", 
		default="median", 
		choices=["median", "mean"],
		help=help_["function"]
	)

	ps.add_argument("--noapply", 
		action="store_true",
		help=help_["noapply"]
	)

	ps.add_argument("--noprogress", action="store_true")

	ps.add_argument("--low_memory_mode", action="store_true", help=help_["low"])

	ps.add_argument("--writeout", default=None, help=help_["write"])

	ps.add_argument("-F", "--freq_scale", 
		action="store_true",
		help=help_["freq_scale"]
	)

	ps.add_argument("-S", "--std",
		action="store_true",
		help=help_["std"]
	)

	ps.add_argument("-b", "--bandpass_polynomial_deg",
		default=0,
		type=int,
		help=help_["bandpass"]
	)

	args = ps.parse_args()

	if args.channels is None and not args.auto:
		raise ValueError("Either -c|--channels or -a|--auto must be specified.")
	
	# Determine the right column to use. By default use CORRECTED_DATA.
	if args.noapply:
		readonly = True
	else:
		readonly = False
	MeasurementSet = tables.table(args.msname, readonly=readonly, ack=False)

	if args.data_column is None:
		if "CORRECTED_DATA" in MeasurementSet.colnames():
			column = "CORRECTED_DATA"
		else:
			column = "DATA"
	else:
		column = args.data_column

	print("Using {}".format(column))
	
	channels = []
	if args.channels is not None:
		channels += channels_to_indices(args.channels)
	if args.auto:
		if args.low_memory_mode:
			channels += auto_clip_(MeasurementSet, args.clip, args.window, column,
				noprogress=args.noprogress
			)
		else:
			channels += auto_clip(MeasurementSet, args.clip, args.window, column,
				mode=args.function,
				writeout=args.writeout,
				scale_freq=args.freq_scale,
				use_single_std=args.std,
				fit_bandpass=args.bandpass_polynomial_deg
			) 
	
	print("Overall channels to flag: {}".format(
		channels
	))

	if not args.noapply:
		try:
			apply_flags(MeasurementSet, channels, args.pad, args.noprogress)
		except Exception:
			raise
			try:
				MeasurementSet.close()
			except Exception:
				pass

	
	sys.exit(0)
