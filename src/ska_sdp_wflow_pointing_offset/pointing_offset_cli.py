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
        vis, freqs, corr_type = read_data_from_rdb_file(args['<args>'][0])

        # What is the output coming from the rdb file that will
        # be passed to the next function?
        clean_vis_data(vis, freqs, corr_type)

if __name__ == "__main__":
    main()
