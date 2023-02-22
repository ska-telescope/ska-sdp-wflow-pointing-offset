# pylint: disable=too-many-arguments, inconsistent-return-statements
""" Regression test for the pointing offset pipeline

"""
import logging
import os
import tempfile
from unittest.mock import patch

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

@patch("ska_sdp_wflow_pointing_offset.read_data._load_ms_tables")
@patch("ska_sdp_wflow_pointing_offset.read_data._open_rdb_file")
@pytest.mark.parametrize(
    "enabled, mode, start_freq, end_freq, auto",
    [
        (
            DEFAULT_RUN,
            "no_frequency_selection",
            None,
            None,
            False,
        ),
        (
            DEFAULT_RUN,
            "frequency_selection",
            8.562e8,
            8.567e8,
            False,
        ),
        (
            DEFAULT_RUN,
            "use_auto_correlation",
            8.562e8,
            8.567e8,
            True,
        ),
    ],
)
def test_wflow_pointing_offset(
    mock_rdb,
    mock_ms,
    enabled,
    mode,
    start_freq,
    end_freq,
    auto,
):
    """
    Main test routine.
    Note: Mock rdb and mock ms need to be kept in the order of
          (rdb, ms) for pytest to pick up correctly.
          Currently, we don't test cases with RFI mask applied,
          Please refer to the unit tests for apply_rfi_mask.

    :param enabled: Is this test enabled?
    :param mode: Which mode it is testing
    :param start_freq: Start frequency (Hz)
    :param end_freq: End frequency (Hz)
    :param auto: Use auto-correlations?
    """

    if not enabled:
        log.warning(
            "test_pointing_offset: test of %s mode is disabled, "
            "use enabled argument to change.",
            mode,
        )
        return True

    with tempfile.TemporaryDirectory() as tempdir:

        log.info("Putting output data into temporary %s.", tempdir)

        mock_rdb.return_value = MockRDBInput()
        mock_ms.return_value = (
            MockAntennaTable(),
            MockBaseTable(),
            MockPolarisationTable(),
            MockSpectralWindowTable(),
            MockSourceTable(),
        )
        outfile = f"{tempdir}/pointing_offsets.txt"

        args = {
            "--start_freq": start_freq,
            "--end_freq": end_freq,
            "--apply_mask": False,
            "--rfi_file": None,
            "--auto": auto,
            "--save_offset": True,
            "--results_dir": tempdir,
            "--rdb": "fake_rdb",
            "--ms": "fake_ms",
        }

        compute_offset(args)

        assert os.path.exists(outfile)

        read_out = numpy.loadtxt(outfile, delimiter=",")
        # Output data shape [nants, 18]
        # Axis 1 is (az, el) * 9 variables
        assert read_out.shape == (3, 18)

        # If we need to save file to tests directory
        if PERSIST:
            log.info("Putting data into test_results directory.")
            test_dir = os.getcwd() + "/test_results"
            os.makedirs(test_dir, exist_ok=True)
            new_name = test_dir + "/pointing_offsets_" + f"{mode}" + ".txt"
            os.replace(outfile, new_name)
