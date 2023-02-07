"""
Command line utility for Pointing Offset Calibration Pipeline.

Usage:
    pointing-offset COMMAND [OBJECTS] [<args>...]
    pointing-offset COMMAND (-h|--help)
    pointing-offset (-h|--help)

Objects:
    ms      Measurement set file
    rdb     RDB file

Commands:
    read        Read file
    clean       Clean Visibility Data

"""

import logging
import sys

from docopt import docopt

from .read_data import (
    read_cross_correlation_visibilities,
    read_data_from_rdb_file,
)
from .coord_support import convert_coordinates

from .workflow import clean_vis_data

LOG = logging.getLogger("ska-sdp-pointing-offset")
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(sys.stdout))

COMMAND = "COMMAND"


def main(argv=None):
    """Run ska-sdp."""
    if argv is None:
        argv = sys.argv[1:]

    args = docopt(__doc__, argv=argv, options_first=True)

    if args[COMMAND] == "read":
        read_clean_data(argv)

    # This doesn't work properly now but need to decide
    # what to do with it
    if args[COMMAND] == "clean":
        clean_vis_data(argv)

    else:
        LOG.error(
            "Command '%s' is not supported. "
            "Run 'pointing-offset --help' to view usage.",
            args[COMMAND],
        )


# Just the first iteration, will split into seperate once
# we have a good idea about the cli
def read_clean_data(argv):
    """Read MS file and run the clean visibilita data"""

    args = docopt(__doc__, argv=argv)
    if args['OBJECTS'] == 'ms':
        print("Just for testing MS!")
        vis, freqs, corr_type = read_cross_correlation_visibilities(args['<args>'][0])
        clean_vis_data(vis, freqs, corr_type)
    elif args['OBJECTS'] == 'rdb':
        print("Just for testing RDB!")
        az, el, timestamps, target_projection, ants, target = read_data_from_rdb_file(args['<args>'][0])

        # Need to add beam centre which will come from beam fitting script
        convert_coordinates(ants, beam_centre, timestamps, target_projection)

if __name__ == "__main__":
    main()
