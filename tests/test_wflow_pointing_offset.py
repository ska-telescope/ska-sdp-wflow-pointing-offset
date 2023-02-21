# pylint: disable=too-many-arguments
""" Regression test for the pointing offset pipeline

"""
import logging
import os
import tempfile
from unittest.mock import MagicMock, patch

import numpy
import pytest

from ska_sdp_wflow_pointing_offset.pointing_offset_cli import compute_offset
from tests.utils import (
    MockAntennaTable,
    MockBaseTable,
    MockPolarisationTable,
    MockRDBInput,
    MockSourceTable,
    MockSpectralWindowTable,
)

log = logging.getLogger("pointing-offset-logger")
log.setLevel(logging.WARNING)

DEFAULT_RUN = True
PERSIST = False


@patch("builtins.open", MagicMock())
@patch("pickle.load")
@patch("ska_sdp_wflow_pointing_offset.read_data._load_ms_tables")
@patch("ska_sdp_wflow_pointing_offset.read_data._open_rdb_file")
@pytest.mark.parametrize(
    "enabled, mode, start_freq, end_freq, apply_mask, auto",
    [
        (
            DEFAULT_RUN,
            "no_frequency_selction",
            None,
            None,
            False,
            False,
        ),
        (
            DEFAULT_RUN,
            "frequency_selection",
            8.562e8,
            8.567e8,
            False,
            False,
        ),
        (
            DEFAULT_RUN,
            "apply_rfi_mask_only",
            8.562e8,
            8.567e8,
            True,
            False,
        ),
        (
            DEFAULT_RUN,
            "use_auto_correlation_only",
            8.562e8,
            8.567e8,
            False,
            True,
        ),
        (
            DEFAULT_RUN,
            "rfi_and_auto",
            8.562e8,
            8.567e8,
            True,
            True,
        ),
    ],
)
def test_wflow_pointing_offset(
    mock_rdb,
    mock_ms,
    mock_rfi_file,
    enabled,
    mode,
    start_freq,
    end_freq,
    apply_mask,
    auto,
):
    """
    Main test routine.
    Note: Mock rdb, ms and rfi_file needs to be kept in the order of
          (rdb, ms, rfi_file) for pytest to pick up correctly.

    :param enabled: Is this test enabled?
    :param mode: Which mode it is testing
    :param start_freq: Start frequency (Hz)
    :param end_freq: End frequency (Hz)
    :param apply_mask: Apply RFI mask?
    :param auto: Use auto-correlations?
    """

    if not enabled:
        log.warning(
            f"test_pointing_offset: test of {mode} mode is disabled, "
            f"use enabled argument to change."
        )
        return True

    test_dir = os.getcwd() + "/test_data/"
    tempdir_root = tempfile.TemporaryDirectory(dir=test_dir)
    tempdir = tempdir_root.name

    log.info(f"Putting output data into temporary {tempdir}.")

    mock_ms.return_value = (
        MockAntennaTable(),
        MockBaseTable(),
        MockPolarisationTable(),
        MockSpectralWindowTable(),
        MockSourceTable(),
    )

    mock_rdb.return_value = MockRDBInput()
    mock_rfi_file.return_value = numpy.array([1, 1, 0, 1, 1])

    args = {
        "--ms": "fake_ms",
        "--rdb": "fake_rdb",
        "--rfi_file": "fake_rfi_file",
        "--start_freq": start_freq,
        "--end_freq": end_freq,
        "--apply_mask": apply_mask,
        "--auto": auto,
        "--save-offset": "True",
    }

    (_,) = compute_offset(args)

    read_out = numpy.loadtxt("pointing_offsets.txt")
    assert len(read_out) == 5
    # other assertions

    # clean up directory
    if PERSIST is False:
        try:
            os.remove(tempdir + "/pointing_offsets.txt")
        except OSError:
            pass

    return
