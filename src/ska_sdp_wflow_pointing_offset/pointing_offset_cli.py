# pylint: disable=too-many-locals
"""Program with many options using docopt for computing pointing offsets.

Usage:
  pointing-offset COMMAND [--ms=FILE] [--save_offset]
                          [--apply_mask] [--fit_tovis]
                          [--rfi_file=FILE] [--results_dir=None]
                          [--start_freq=None] [--end_freq=None]
                          [(--bw_factor <bw_factor>) [<bw_factor>...]]

Commands:
  compute   Runs all required routines for computing the
  pointing offsets.

Options:
  -h --help            show this help message and exit
  -q --quiet           report only file names

  --ms=FILE            Measurement set file
  --fit_tovis          Fit primary beam to visibilities instead of antenna
                       gains (Optional) [default:False]
  --apply_mask         Apply Mask (Optional) [default:False]
  --rfi_file=FILE      RFI file (Optional)
  --save_offset        Save the Offset Results (Optional) [default:False]
  --results_dir=None   Directory where the results need to be saved (Optional)
  --start_freq=None    Start Frequency (Optional)
  --end_freq=None      End Frequency (Optional)
  --bw_factor          Beamwidth factor [default:0.976, 1.098]

"""
import logging
import os
import sys
from pathlib import PurePosixPath

from docopt import docopt

from ska_sdp_wflow_pointing_offset.beam_fitting import fit_primary_beams
from ska_sdp_wflow_pointing_offset.export_data import (
    export_pointing_offset_data,
)
from ska_sdp_wflow_pointing_offset.freq_select import clean_vis_data
from ska_sdp_wflow_pointing_offset.read_data import read_visibilities
from ska_sdp_wflow_pointing_offset.utils import (
    compute_gains,
    get_gain_results,
    gt_single_plot,
)

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
        if args["--ms"]:
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

    def _safe_float(number):
        return float(number)

    if args["--apply_mask"]:
        if not args["--rfi_file"]:
            raise ValueError("RFI File is required!!")

    # Set beamwidth factor
    if args["--bw_factor"]:
        beamwidth_factor = args["<bw_factor>"]
        beamwidth_factor = list(map(_safe_float, beamwidth_factor))
        if len(beamwidth_factor) == 1:
            beamwidth_factor.append(beamwidth_factor[0])
    else:
        # We would use the values for the MeerKAT as known in April 2023.
        beamwidth_factor = [0.976, 1.098]
    log.info(
        "Beamwidth factor: %f %f", beamwidth_factor[0], beamwidth_factor[1]
    )

    # Get visibilities
    vis, source_offsets, ants = read_visibilities(
        msname=args["--ms"],
        start_freq=args["--start_freq"],
        end_freq=args["--end_freq"],
    )

    # Optionally select frequency ranges and/or apply RFI mask
    avg_vis, selected_freqs = clean_vis_data(
        vis=vis,
        start_freq=args["--start_freq"],
        end_freq=args["--end_freq"],
        apply_mask=args["--apply_mask"],
        rfi_filename=args["--rfi_file"],
    )

    # Perform gain calibration if fitting primary beams to antenna gains
    if args["fit_tovis"]:
        y_param = avg_vis.vis.data
        weights = avg_vis.weights.data
    else:
        gt_list = compute_gains(vis=avg_vis)
        timeseries, amp, phase_rel, residual, weights = get_gain_results(
            gt_list=gt_list
        )
        y_param = amp

        # Save plot of computed gains
        plot_name = os.path.join(
            PurePosixPath(args["--ms"]).parent.as_posix(),
            "computed_gains",
        )
        gt_single_plot(gt_list=gt_list, plot_name=plot_name)

    # Fit primary beams to visibilities or gains
    fitted_results = fit_primary_beams(
        y_param=y_param,
        freqs=selected_freqs,
        weights=weights,
        ants=ants,
        x_param=source_offsets,
        beamwidth_factor=beamwidth_factor,
        fit_tovis=args["--fit_tovis"],
    )

    # fitted_results = fit_primary_beams(
    #    avg_vis=avg_vis, #y_param
    #    freqs=selected_freqs,
    #    corr_type=corr_type,
    #    vis_weights=vis_weights,
    #    ants=ants,
    #    source_offsets=source_offsets,  #x_param
    #    beamwidth_factor=beamwidth_factor,
    #    fit_tovis=args["--fit_tovis"],
    # )

    """
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
    """


if __name__ == "__main__":
    main()
