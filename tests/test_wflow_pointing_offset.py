""" Regression test for the pointing offset pipeline

"""
import logging
import os
import tempfile
from unittest.mock import MagicMock, patch

import numpy
import pytest

from ska_sdp_wflow_pointing_offset import cli_parser, compute_offset

log = logging.getLogger("pointing-offset-logger")
log.setLevel(logging.WARNING)

default_run = True
persist = False
NTIMES = 4
NANTS = 6
NCHAN = 5


@patch("builtins.open", MagicMock())
@patch("pickle.load")
@patch("ska_sdp_wflow_pointing_offset.read_data._load_ms_tables")
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
    enabled,
    start_freq,
    end_freq,
    apply_mask,
    split_pol,
    auto,
    mock_ms,
    mock_rdb,
    mock_rfi,
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

    # MS Tables to read
    mock_ms.return_value = (
        MockAntennaTable(),
        MockBaseTable(),
        MockPolarisationTable(),
        MockSpectralWindowTable(),
    )

    mock_rdb.return_value = 0
    mock_rfi.return_value = numpy.array([1, 1, 0, 1, 1])

    parser = cli_parser()
    args = parser.parse_args(
        [
            "--msname",
            "fake_ms",
            "--metadata",
            "fake_rdb",
            "--rfi_file",
            "fake_rfi",
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
            "--save-offset",
            "True",
        ]
    )

    (_,) = compute_offset(args)

    read_out = np.loadtxt("pointing_offsets.txt")
    assert len(read_out) == NANTS
    # other assertions

    # clean up directory
    if persist is False:
        try:
            os.remove(tempdir + "/pointing_offsets.txt")
        except OSError:
            pass
