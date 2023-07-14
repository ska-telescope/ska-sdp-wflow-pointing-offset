# pylint: disable=too-many-locals,too-many-branches
# pylint: disable=too-many-statements
"""Program with many options using docopt for computing pointing offsets.

Usage:
  pointing-offset COMMAND [--msdir=DIR] [--save_offset]
                          [--apply_mask] [--use_weights]
                          [--fit_to_vis] [--rfi_file=FILE]
                          [--results_dir=None] [--start_freq=None]
                          [--end_freq=None] [--num_chunks=<int>]
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
  --num_chunks=<int>    Number of frequency chunks for gain calibration
                        if fitting primary beams to gain amplitudes
                        [default:16]
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

from ska_sdp_wflow_pointing_offset.array_data_func import (
    ExtractPerScan,
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

    # Set threshold on fitted beamwidth
    if args["--thresh_width"]:
        thresh_width = float(args["--thresh_width"])
    else:
        thresh_width = 1.5

    # Set number of frequency chunks for gain calibration
    if args["--num_chunks"]:
        num_chunks = int(args["--num_chunks"])
    else:
        num_chunks = 16

    log.info(
        "Beamwidth factor: %f %f", beamwidth_factor[0], beamwidth_factor[1]
    )
    log.info(
        "Maximum fitted beamwidth to expected beamwidth: %f", thresh_width
    )
    if not args["--fit_to_vis"]:
        log.info(
            "Number of frequency chunks for gain calibration: %d", num_chunks
        )

    # Get visibilities and optionally apply RFI mask and/or select
    # frequency range of interest
    if args["--apply_mask"]:
        if not args["--rfi_file"]:
            raise ValueError("RFI File is required!!")

    (
        vis_list,
        source_offset_list,
        pointing_timestamps_list,
        ants,
        target,
    ) = read_batch_visibilities(
        args["--msdir"],
        args["--apply_mask"],
        args["--rfi_file"],
        args["--start_freq"],
        args["--end_freq"],
    )

    # Get the datasets required for the fitting and fit for the
    # pointing offsets
    params = ExtractPerScan(
        vis_list, source_offset_list, ants, args["--time_avg"]
    )
    if args["--fit_to_vis"]:
        x_per_scan, y_per_scan, _, freqs = params.from_vis()
        fitted_beams = SolveForOffsets(
            x_per_scan, y_per_scan, freqs, beamwidth_factor, ants, thresh_width
        ).fit_to_visibilities()
    else:
        x_per_scan, y_per_scan, weights_per_scan, freqs = params.from_gains(
            num_chunks
        )
        if not args["--use_weights"]:
            weights_per_scan = numpy.ones(numpy.shape(weights_per_scan))
        fitted_beams = SolveForOffsets(
            x_per_scan, y_per_scan, freqs, beamwidth_factor, ants, thresh_width
        ).fit_to_gains(weights_per_scan, num_chunks)

    # Compute the weighted-average of the valid pointing offsets
    output_offset = weighted_average(
        ants,
        fitted_beams,
        target,
        numpy.concatenate(pointing_timestamps_list),
        num_chunks,
    )

    # Save the fitted parameters and computed offsets
    # To be addressed with ORC-192 by writing the fitted
    # offsets into the ska-sdp-datamodels PointingTable
    # for the long term
    if args["--save_offset"]:
        log.info("Writing fitted parameters and computed offsets to file...")
        if args["--results_dir"] is None:
            # Save to the location of the measurement set
            results_file = os.path.join(
                args["--msdir"], "pointing_offsets.txt"
            )
            export_pointing_offset_data(results_file, output_offset)
        else:
            # Save to the user-set directory
            results_file = os.path.join(
                args["--results_dir"], "pointing_offsets.txt"
            )
            export_pointing_offset_data(results_file, output_offset)

        log.info(
            "Fitted parameters and computed offsets written to %s",
            results_file,
        )
    else:
        if output_offset.shape[0] < 10:
            log.info(
                "The fitted parameters and "
                "computed offsets are printed on screen."
            )
            for i, line in enumerate(output_offset):
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
