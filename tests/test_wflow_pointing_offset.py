""" Regression test for the pointing offset pipeline

"""
import logging
import os
import tempfile

import pytest

from ska_sdp_wflow_pointing_offset import cli_parser

log = logging.getLogger("pointing-offset-logger")
log.setLevel(logging.WARNING)

default_run = True
persist = False


@pytest.mark.parametrize(
    "enabled, start_freq, end_freq, apply_mask, split_pol, auto",
    [
        (
            default_run,
            0.8e9,
            1.5e9,
            True,
            True,
            True,
        ),
        # add more test configurations here
    ],
)
def test_wflow_pointing_offset(
    enabled, start_freq, end_freq, apply_mask, split_pol, auto
):
    """
    Main test routine.

    :param enabled:
    :param start_freq:
    :param end_freq:
    :param apply_mask:
    :param split_pol:
    :param auto:
    :return:
    """

    if not enabled:
        log.warning(
            f"test_mid_simulation: test of {mode} mode is disabled, use enabled argument to change"
        )
        return True

    test_dir = os.getcwd() + "/test_data/"
    tempdir_root = tempfile.TemporaryDirectory(dir=test_dir)
    tempdir = tempdir_root.name

    log.info(f"Putting output data into temporary {tempdir}.")

    msname = test_dir + "/test_meerkat.ms"
    metadata_name = test_dir + "/test_meerkat.rdb"
    rfi_filename = test_dir + "/rfi.pickle"

    parser = cli_parser()
    args = parser.parse_args(
        [
            "--msname",
            msname,
            "--metadata",
            metadata_name,
            "--rfi_file",
            rfi_filename,
            "--start_freq",
            f"{start_freq}",
            "--end_freq",
            f"{end_freq}",
            "--apply_mask",
            f"{apply_mask}",
            "--split_pol",
            f"{split_pol}",
            "--auto",
            f"{auto}",
        ]
    )

    # output = main_workflow(args)

    # asserts

    # clean up directory
    if persist is False:
        try:
            os.remove(tempdir + "/output_file*")
        except OSError:
            pass
