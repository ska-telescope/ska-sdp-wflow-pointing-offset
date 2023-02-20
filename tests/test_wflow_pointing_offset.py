""" Regression test for the pointing offset pipeline

"""
import logging
import os
import tempfile
from unittest.mock import MagicMock, patch

import numpy
import pytest
from conftest import (
    MockAntennaTable,
    MockBaseTable,
    MockPolarisationTable,
    MockRDBInput,
    MockSourceTable,
    MockSpectralWindowTable,
)

from ska_sdp_wflow_pointing_offset import compute_offset, construct_antennas

log = logging.getLogger("pointing-offset-logger")
log.setLevel(logging.WARNING)

default_run = True
persist = False


@patch("builtins.open", MagicMock())
@patch("pickle.load")
@patch("ska_sdp_wflow_pointing_offset.read_data._load_ms_tables")
@patch("ska_sdp_wflow_pointing_offset.read_data._open_rdb_file")
@pytest.mark.parametrize(
    "enabled, start_freq, end_freq, apply_mask, auto",
    [
        (
            default_run,
            None,
            None,
            False,
            False,
        ),
        (
            default_run,
            0.8e9,
            1.5e9,
            False,
            False,
        ),
        (
            default_run,
            0.8e9,
            1.5e9,
            True,
            False,
        ),
        (
            default_run,
            0.8e9,
            1.5e9,
            False,
            True,
        ),
        (
            default_run,
            0.8e9,
            1.5e9,
            True,
            True,
        ),
    ],
)
def test_wflow_pointing_offset(
    enabled,
    start_freq,
    end_freq,
    apply_mask,
    auto,
    mock_ms,
    mock_rdb,
    mock_rfi,
):
    """
    Main test routine.

    :param enabled: Is this test enabled?
    :param start_freq: Start frequency (Hz)
    :param end_freq: End frequency (Hz)
    :param apply_mask: Apply RFI mask?
    :param auto: Use auto-correlations?
    """

    if not enabled:
        log.warning(
            f"test_pointing_offset: test of {mode} mode is disabled, use enabled argument to change"
        )
        return True

    test_dir = os.getcwd() + "/test_data/"
    tempdir_root = tempfile.TemporaryDirectory(dir=test_dir)
    tempdir = tempdir_root.name

    log.info(f"Putting output data into temporary {tempdir}.")

    # MS Tables to read -- this need to be moved to some config first
    mock_ms.return_value = (
        MockAntennaTable(),
        MockBaseTable(),
        MockPolarisationTable(),
        MockSpectralWindowTable(),
        MockSourceTable(),
    )

    mock_rdb.return_value = MockRDBInput()
    mock_rfi.return_value = numpy.array([1, 1, 0, 1, 1])

    args = {
        "--ms": "fake_ms",
        "--rdb": "fake_rdb",
        "--rfi_file": "fake_rfi",
        "--start_freq": f"{start_freq}",
        "--end_freq": f"{end_freq}",
        "--apply_mask": f"{apply_mask}",
        "--auto": f"{auto}",
        "--save-offset": "True",
    }

    (_,) = compute_offset(args)

    read_out = numpy.loadtxt("pointing_offsets.txt")
    assert len(read_out) == 5
    # other assertions

    # clean up directory
    if persist is False:
        try:
            os.remove(tempdir + "/pointing_offsets.txt")
        except OSError:
            pass
