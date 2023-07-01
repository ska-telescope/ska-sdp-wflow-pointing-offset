# pylint: disable=too-many-locals,too-many-branches
"""Program with many options using docopt for computing pointing offsets.

Usage:
  pointing-offset COMMAND [--ms=FILE] [--save_offset]
                          [--msdir=DIR]
                          [--apply_mask] [--fit_to_vis]
                          [--rfi_file=FILE] [--results_dir=None]                          
                          [--start_freq=None] [--end_freq=None]
                          [(--bw_factor <bw_factor>) [<bw_factor>...]]
                          [--thresh_width=<float>]

Commands:
  compute   Runs all required routines for computing the
  pointing offsets.

Options:
  -h --help            show this help message and exit
  -q --quiet           report only file names

  --ms=FILE             Measurement set file
  --msdir=DIR           Directory including Measurement set files
  --fit_to_vis          Fit primary beam to visibilities instead of antenna
                        gains (Optional) [default:False]
  --apply_mask          Apply mask (Optional) [default:False]
  --rfi_file=FILE       RFI file (Optional)
  --save_offset         Save the offset results (Optional) [default:False]
  --results_dir=None    Directory where the results need to be saved (Optional)
  --start_freq=None     Start frequency in MHz (Optional)
  --end_freq=None       End frequency in MHz (Optional)
  --bw_factor           Beamwidth factor [default:0.976, 1.098]
  --thresh_width=<float>  The maximum ratio of the fitted to expected beamwidth
                          [default:1.5]

"""
import datetime
import logging
import os
import sys
import time
from pathlib import PurePosixPath

from docopt import docopt

from ska_sdp_wflow_pointing_offset.beam_fitting import SolveForOffsets
from ska_sdp_wflow_pointing_offset.export_data import (
    export_pointing_offset_data,
)
from ska_sdp_wflow_pointing_offset.read_data import read_visibilities,read_batch_visibilities
from ska_sdp_wflow_pointing_offset.utils import compute_gains, gt_single_plot

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
        if args["--ms"] or args["--msdir"]:
            compute_offset(args)
        else:
            raise ValueError("Measurement set is required!!")

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

    if args["--ms"]:
        vis, source_offset, actual_pointing_el, ants = read_visibilities(
            args["--ms"],
            args["--apply_mask"],
            args["--rfi_file"],
            args["--start_freq"],
            args["--end_freq"],
        )
    elif args["--msdir"]:
        vis, source_offset, actual_pointing_el, ants = read_batch_visibilities(
            args["--msdir"],
            args["--apply_mask"],
            args["--rfi_file"],
            args["--start_freq"],
            args["--end_freq"],
        )
        

    if args["--fit_to_vis"]:
        y_param = vis
    else:
        # Solve for the antenna gains
        log.info("Solving for the antenna complex gains...")
        gt_list = compute_gains(vis)
        y_param = gt_list

        # Save gain plot
        # plot_name = os.path.join(
        #     PurePosixPath(args["--ms"]).parent.as_posix(),
        #     "computed_gains",
        # )
        # gt_single_plot(gt_list, plot_name)

    # Solve for the pointing offsets
    init_results = SolveForOffsets(
        source_offset,
        actual_pointing_el,
        y_param,
        beamwidth_factor,
        ants,
        thresh_width,
    )
    if args["--fit_to_vis"]:
        fitted_results = init_results.fit_to_visibilities()
    else:
        fitted_results = init_results.fit_to_gains()

    # Save the fitted parameters and computed offsets
    if args["--save_offset"]:
        log.info("Writing fitted parameters and computed offsets to file...")
        if args["--results_dir"] is None:
            # Save to the location of the measurement set
            results_file = os.path.join(
                PurePosixPath(args["--ms"]).parent.as_posix(),
                "pointing_offsets.txt",
            )
            export_pointing_offset_data(
                results_file,
                fitted_results,
            )
        else:
            # Save to the user-set directory
            results_file = os.path.join(
                args["--results_dir"], "pointing_offsets.txt"
            )
            export_pointing_offset_data(
                results_file,
                fitted_results,
            )
        log.info(
            "Fitted parameters and computed offsets written to %s",
            results_file,
        )
    else:
        if fitted_results.shape[0] < 10:
            log.info(
                "The fitted parameters and "
                "computed offsets are printed on screen."
            )
            for i, line in enumerate(fitted_results):
                log.info("Offset array for antenna %i is: %s", i, line)
        else:
            log.info(
                "There are too many antennas. "
                "Please set --save_offsets as True "
                "to save the offsets to a file. "
            )

    end = time.time()
    log.info(
        "\nProcess finished in %s", (datetime.timedelta(seconds=end - begin))
    )


if __name__ == "__main__":
    main()