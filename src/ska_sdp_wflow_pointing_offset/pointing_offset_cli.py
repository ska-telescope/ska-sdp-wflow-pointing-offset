# pylint: disable=too-many-locals,too-many-branches
# pylint: disable=too-many-statements
"""Program with many options using docopt for computing pointing offsets.

Usage:
  pointing-offset COMMAND [--msdir=DIR] [--save_offset]
                          [--apply_mask] [--use_weights]
                          [--fit_to_vis] [--rfi_file=FILE]
                          [--results_dir=None] [--start_freq=None]
                          [--end_freq=None]
                          [(--bw_factor <bw_factor>) [<bw_factor>...]]
                          [--thresh_width=<float>][--time_avg=None]

Commands:
  compute   Runs all required routines for computing the
  pointing offsets.

Options:
  -h --help            show this help message and exit
  -q --quiet           report only file names

  --msdir=DIR           Directory including Measurement set files
  --fit_to_vis          Fit primary beam to visibilities instead of antenna
                        gains (Optional) [default:False]
  --apply_mask          Apply mask (Optional) [default:False]
  --use_weights         Use weights when fitting the primary beams to the
                        gain amplitudes (Optional) [default:False]
  --rfi_file=FILE       RFI file (Optional)
  --save_offset         Save the offset results (Optional) [default:False]
  --results_dir=None    Directory where the results need to be saved (Optional)
  --start_freq=None     Start frequency in MHz (Optional)
  --end_freq=None       End frequency in MHz (Optional)
  --bw_factor           Beamwidth factor [default:0.976, 1.098]
  --thresh_width=<float>  The maximum ratio of the fitted to expected beamwidth
                          [default:1.5]
  --time_avg=None       Perform no, median, or mean time-averaging of the
                        gain amplitudes when fitting to gains. These options
                        can be set with None, "median", or "mean".

"""
import datetime
import logging
import os
import sys
import time

import numpy
from docopt import docopt
from katpoint import wrap_angle

from ska_sdp_wflow_pointing_offset.array_data_func import (
    compute_gains,
    time_avg_amp,
    weighted_average,
)
from ska_sdp_wflow_pointing_offset.beam_fitting import SolveForOffsets
from ska_sdp_wflow_pointing_offset.export_data import (
    export_pointing_offset_data,
)
from ska_sdp_wflow_pointing_offset.read_data import read_batch_visibilities

log = logging.getLogger("ska-sdp-pointing-offset")
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))

COMMAND = "COMMAND"


def main():
    """
    Run pointing offset calibration routines
    """

    args = docopt(__doc__)

    if args[COMMAND] == "compute":
        if args["--msdir"]:
            compute_offset(args)
        else:
            raise ValueError(
                "Directory containing measurement sets is required!!"
            )

    else:
        log.error(
            "Command '%s' is not supported. "
            "Run 'pointing-offset --help' to view usage.",
            args[COMMAND],
        )


def compute_offset(args):
    """
    Reads visibilities from a measurement set and optionally
    applies RFI mask and selects some frequency ranges, and
    fits primary beams to the "RFI-free" visibilities to
    obtain the pointing offsets.

    :param args: required and optional arguments
    """
    begin = time.time()

    def _safe_float(number):
        return float(number)

    # Set beamwidth factor
    if args["--bw_factor"]:
        beamwidth_factor = args["<bw_factor>"]
        beamwidth_factor = list(map(_safe_float, beamwidth_factor))
        if len(beamwidth_factor) == 1:
            beamwidth_factor.append(beamwidth_factor[0])
    else:
        # We would use the values for the MeerKAT as known in April 2023.
        beamwidth_factor = [0.976, 1.098]

    if args["--thresh_width"]:
        thresh_width = float(args["--thresh_width"])
    else:
        thresh_width = 1.5

    log.info(
        "Beamwidth factor: %f %f", beamwidth_factor[0], beamwidth_factor[1]
    )
    log.info(
        "Maximum fitted beamwidth to expected beamwidth: %f", thresh_width
    )

    # Get visibilities and optionally apply RFI mask and/or select
    # frequency range of interest
    if args["--apply_mask"]:
        if not args["--rfi_file"]:
            raise ValueError("RFI File is required!!")

    (
        vis_list,
        source_offset_list,
        offset_timestamps,
        ants,
        target,
    ) = read_batch_visibilities(
        args["--msdir"],
        args["--apply_mask"],
        args["--rfi_file"],
        args["--start_freq"],
        args["--end_freq"],
    )
    freqs = numpy.zeros((1))
    x_per_scan = numpy.zeros((len(source_offset_list), len(ants), 2))
    y_per_scan = numpy.zeros((len(ants), len(vis_list)))
    weights_per_scan = numpy.zeros((len(ants), len(vis_list)))
    offset_timestamps = numpy.concatenate(offset_timestamps)
    for scan, (vis, source_offset) in enumerate(
        zip(vis_list, source_offset_list)
    ):
        # Average antenna pointings in time
        x_per_scan[scan] = source_offset.mean(axis=0)
        if args["--fit_to_vis"]:
            # To be looked at in detail in ORC-1572
            # Get autocorrelations only
            get_autocorr = vis.antenna1.data == vis.antenna2.data
            vis_amp = numpy.abs(vis.vis.data)
            vis_amp = vis_amp[:, get_autocorr, :, :]

            # Visibilities have shape(ntimes, nants, nfreqs, npols)
            # Get the parallel hands polarisation visibilities
            if len(vis.polarisation.data) == 2:
                # Get (XX and YY
                vis_amp = numpy.array(
                    [vis_amp[:, :, :, 0], vis_amp[:, :, :, 1]]
                )
                vis_amp = numpy.moveaxis(vis_amp, 0, 3)
            elif len(vis.polarisation.data) == 4:
                vis_amp = numpy.array(
                    [vis_amp[:, :, :, 0], vis_amp[:, :, :, 3]]
                )
                vis_amp = numpy.moveaxis(vis_amp, 0, 3)

            # Average in frequency and polarisation
            vis_amp = vis_amp.mean(axis=(2, 3))

            # No or time-averaging of visibility amplitudes
            vis_amp = time_avg_amp(vis_amp, time_avg=args["--time_avg"])
            if scan == 0:
                # We want to use the frequency at the higher end of the
                # frequency for better pointing accuracy
                freqs[scan] = numpy.squeeze(vis.frequency.data[-1])
            y_per_scan[:, scan] = vis_amp
        else:
            # Solve for the un-normalised G terms for each scan
            log.info(
                "Solving for the antenna complex gains for scan %d", scan + 1
            )
            gt_list = compute_gains(vis, 1)

            # Gains have shape (ntimes, nants, nfreqs, receptor1, receptor2)
            # pylint:disable=fixme
            # TODO: Yet to concatenate list of gain tables
            gt_amp = numpy.abs(gt_list[0].gain.data)
            gt_amp = numpy.dstack(
                (gt_amp[:, :, :, 0, 0], gt_amp[:, :, :, 1, 1])
            )
            gt_weights = gt_list[0].weight.data
            gt_weights = numpy.dstack(
                (gt_weights[:, :, :, 0, 0], gt_weights[:, :, :, 1, 1])
            )

            # Average in polarisation
            gt_amp = gt_amp.mean(axis=2)
            gt_weights = gt_weights.mean(axis=2)

            # Perform no or time-averaging of gain amplitudes and weights
            gt_amp = time_avg_amp(gt_amp, time_avg=args["--time_avg"])
            gt_weights = time_avg_amp(gt_weights, time_avg=args["--time_avg"])

            if scan == 0:
                freqs[scan] = numpy.squeeze(gt_list[0].frequency.data)
            y_per_scan[:, scan] = gt_amp
            weights_per_scan[:, scan] = gt_weights

    # Solve for the pointing offsets
    initial_beams = SolveForOffsets(
        x_per_scan, y_per_scan, freqs, beamwidth_factor, ants, thresh_width
    )
    if args["--fit_to_vis"]:
        fitted_beams = initial_beams.fit_to_visibilities()
    else:
        fitted_beams = initial_beams.fit_to_gains(
            weights_per_scan, args["--use_weights"]
        )

    # Compute the weighted-average of the valid fitted offsets
    azel_offset = numpy.degrees(
        wrap_angle(weighted_average(ants, fitted_beams))
    )

    # Compute cross-elevation offset as azimuth offset * cosine (el). We
    # use the target elevation as the elevation
    target_el = numpy.full(len(ants), numpy.nan)
    antenna_names = []
    for i, antenna in enumerate(ants):
        target_azel = target.azel(
            timestamp=numpy.median(offset_timestamps), antenna=antenna
        )
        target_el[i] = numpy.degrees(target_azel)[1]
        antenna_names.append(antenna.name)
    cross_el = azel_offset[:, 0] * numpy.degrees(
        numpy.cos(numpy.radians(target_el))
    )

    # Output final offsets of interest in azimuth , elevation and cross-el
    # offsets in units of arcminutes
    pointing_offset = numpy.column_stack(
        (
            antenna_names,
            azel_offset[:, 0] * 60.0,
            azel_offset[:, 1] * 60.0,
            cross_el * 60.0,
        )
    )

    # Save the fitted parameters and computed offsets
    if args["--save_offset"]:
        log.info("Writing fitted parameters and computed offsets to file...")
        if args["--results_dir"] is None:
            # Save to the location of the measurement set
            results_file = os.path.join(
                args["--msdir"], "pointing_offsets.txt"
            )
            export_pointing_offset_data(results_file, pointing_offset)
        else:
            # Save to the user-set directory
            results_file = os.path.join(
                args["--results_dir"], "pointing_offsets.txt"
            )
            export_pointing_offset_data(results_file, pointing_offset)

        log.info(
            "Fitted parameters and computed offsets written to %s",
            results_file,
        )
    else:
        if azel_offset.shape[0] < 10:
            log.info(
                "The fitted parameters and "
                "computed offsets are printed on screen."
            )
            for i, line in enumerate(pointing_offset):
                log.info("Offset array for antenna %i is: %s", i, line)
        else:
            log.info(
                "There are too many antennas. "
                "Please set --save_offset to save "
                "the offsets to a file. "
            )

    end = time.time()
    log.info(
        "\nProcess finished in %s", (datetime.timedelta(seconds=end - begin))
    )


if __name__ == "__main__":
    main()
