"""Program with many options using docopt for computing pointing offsets.

Usage:
  pointing-offset COMMAND [--ms=FILE] [--rdb=FILE] [--save_offset]
                          [--apply_mask] [--rfi_file=FILE]
                          [--results_dir=None] [--start_freq=None]
                          [--end_freq=None] [--auto]

Commands:
  compute   Runs all required routines for computing the
  pointing offsets.

Options:
  -h --help            show this help message and exit
  -q --quiet           report only file names

  --rdb=FILE           RDB file
  --ms=FILE            Measurement set file
  --apply_mask         Apply Mask (Optional) [default:False]
  --rfi_file=FILE      RFI file (Optional)
  --save_offset        Save the Offset Results (Optional) [default:False]
  --results_dir=None   Directory where the results need to be saved (Optional)
  --start_freq=None    Start Frequency (Optional)
  --end_freq=None      End Frequency (Optional)
  --auto               Auto-correlation visibilities (Optional) [default:False]

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
from ska_sdp_wflow_pointing_offset.read_data import (
    read_data_from_rdb_file,
    read_visibilities,
)

LOG = logging.getLogger("ska-sdp-pointing-offset")
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(sys.stdout))

COMMAND = "COMMAND"


def main():
    """
    Run pointing offset calibration routines
    """

    args = docopt(__doc__)

    if args[COMMAND] == "compute":
        if args["--ms"] and args["--rdb"]:
            compute_offset(args)
        else:
            raise ValueError("MS and RDB files are required!!")

    else:
        LOG.error(
            "Command '%s' is not supported. "
            "Run 'pointing-offset --help' to view usage.",
            args[COMMAND],
        )


def compute_offset(args):
    """
    Reads visibilities from a measurement set, metadata from
    RDB file, optionally applies RFI mask and selects some
    frequency ranges, and fits primary beams to the "RFI-free"
    visibilities to obtain the pointing offsets.

    :param args: required and optional arguments
    """

    # Get visibilities
    vis, freqs, corr_type, vis_weight, target = read_visibilities(
        msname=args["--ms"], auto=args["--auto"]
    )

    # Get the metadata
    (
        timestamps,
        target_projection,
        ants,
        dish_coord,
    ) = read_data_from_rdb_file(rdbfile=args["--rdb"], auto=args["--auto"])

    # Optionally select frequency ranges and/or apply RFI mask
    if args["--apply_mask"]:
        if not args["--rfi_file"]:
            raise ValueError("RFI File is required!!")

    avg_vis, selected_freqs, vis_weight, corr_type = clean_vis_data(
        vis,
        freqs,
        corr_type,
        vis_weight=vis_weight,
        start_freq=args["--start_freq"],
        end_freq=args["--end_freq"],
        apply_mask=args["--apply_mask"],
        rfi_filename=args["--rfi_file"],
    )

    # Fit primary beams to visibilities
    fitted_results = fit_primary_beams(
        avg_vis=avg_vis,
        freqs=selected_freqs,
        timestamps=timestamps,
        corr_type=corr_type,
        vis_weight=vis_weight,
        ants=ants,
        dish_coordinates=dish_coord,
        target=target,
        target_projection=target_projection,
        beamwidth_factor=ants[0].beamwidth,
        auto=str(args["--auto"]),
    )

    # Save the fitted parameters and computed offsets
    if args["--save_offset"]:
        LOG.info("Writing fitted parameters and computed offsets to file...")
        if args["--results_dir"] is None:
            # Save to the location of the measurement set
            results_file = os.path.join(
                PurePosixPath(args["--ms"]).parent.as_posix(),
                "pointing_offsets.txt",
            )
            export_pointing_offset_data(
                results_file,
                offset=fitted_results,
            )
        else:
            # Save to the user-set directory
            results_file = os.path.join(
                args["--results_dir"], "pointing_offsets.txt"
            )
            export_pointing_offset_data(
                results_file,
                offset=fitted_results,
            )
        LOG.info(
            "Fitted parameters and computed offsets written to %s",
            results_file,
        )


if __name__ == "__main__":
    main()
