# pylint: disable=too-many-arguments, inconsistent-return-statements
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
            "test_pointing_offset: test of %s mode is disabled, "
            "use enabled argument to change.",
            mode,
        )
        return True

    test_dir = os.getcwd() + "/test_data/"
    with tempfile.TemporaryDirectory(dir=test_dir) as tempdir:

        log.info("Putting output data into temporary %s.", tempdir)
        os.makedirs(tempdir, exist_ok=True)

        mock_rdb.return_value = MockRDBInput()
        mock_ms.return_value = (
            MockAntennaTable(),
            MockBaseTable(),
            MockPolarisationTable(),
            MockSpectralWindowTable(),
            MockSourceTable(),
        )
        mock_rfi_file.return_value = numpy.array([1, 1, 0, 1, 1])

        args = {
            "--start_freq": start_freq,
            "--end_freq": end_freq,
            "--apply_mask": apply_mask,
            "--auto": auto,
            "--save_offset": True,
            "--results_dir": tempdir,
            "--rdb": "fake_rdb",
            "--ms": "fake_ms",
            "--rfi_file": "fake_rfi_file",
        }

        compute_offset(args)

        outfile = f"{tempdir}/pointing_offsets.txt"
        assert os.path.exists(outfile)

        read_out = numpy.loadtxt(outfile)
        # Output data shape [nants, 18]
        # Axis 1 is (az, el) * 9 variables
        if apply_mask:
            assert read_out.shape(1, 18)
        else:
            assert read_out.shape(3, 18)

    # clean up directory
    if PERSIST is False:
        try:
            os.remove(outfile)
        except OSError:
            pass
