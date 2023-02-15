"""Example of program with many options using docopt.

Usage:
  pointing-offset COMMAND [--ms=FILE] [--rdb=FILE] [--save_offset=False] [--results_dir=None] [--start_freq=None] [--end_freq=None]
  pointing-offset --version

Commands:
  compute   Compute all calculations

Options:
  -h --help            show this help message and exit
  -q --quiet           report only file names

"""
import logging
import sys

from docopt import docopt

from ska_sdp_wflow_pointing_offset.beam_fitting import fit_primary_beams
from ska_sdp_wflow_pointing_offset.coord_support import convert_coordinates
from ska_sdp_wflow_pointing_offset.read_data import (
    read_data_from_rdb_file,
    read_visibilities,
)
from src.ska_sdp_wflow_pointing_offset.workflow import clean_vis_data

LOG = logging.getLogger("ska-sdp-pointing-offset")
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(sys.stdout))

COMMAND = "COMMAND"


def main():
    """Run ska-sdp."""

    args = docopt(__doc__)





    if args[COMMAND] == "compute":
        print("I am in here!!!")
        if args['--ms'] and args['--rdb']:
            compute_everything(args)
        else:
            raise ValueError("MS and RDB are required!!")


    else:
        LOG.error(
            "Command '%s' is not supported. "
            "Run 'pointing-offset --help' to view usage.",
            args[COMMAND],
        )


def compute_everything(args):
    """."""

    # Get visibilities
    vis, freqs, corr_type, dish_diam, vis_weight = read_visibilities(
        msname=args.msname, auto=args.auto
    )

    # Get the metadata
    (
        az,
        el,
        timestamps,
        target_projection,
        ants,
        target,
        dish_coord,
    ) = read_data_from_rdb_file(rdbfile=args.metadata, auto=args.auto)

    # Get RFI-free visibilities
    avg_vis, selected_freqs, vis_weight, corr_type = clean_vis_data(
        vis,
        freqs,
        corr_type,
        vis_weight=vis_weight,
        start_freq=args.start_freq,
        end_freq=args.end_freq,
        apply_mask=args.apply_mask,
        rfi_filename=args.rfi_file,
        split_pol=args.split_pol,
    )

    # Fit primary beams to visibilities
    fit_primary_beams(
        avg_vis=avg_vis,
        freqs=freqs,
        timestamps=timestamps,
        corr_type=corr_type,
        vis_weight=vis_weight,
        ants=ants,
        dish_diameter=dish_diam,
        dish_coordinates=dish_coord,
        target=target,
        target_projection=target_projection,
        beamwidth_factor=ants[0].beamwidth,
        auto=args.auto,
        split_pol=args.split_pol,
        save_offset=true,
        # Optional - Don't need it when it is None
        results_dir=None,
    )


if __name__ == "__main__":
    main()
