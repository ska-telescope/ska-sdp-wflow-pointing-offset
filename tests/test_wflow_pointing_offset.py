""" Regression test for the pointing offset pipeline

"""
import logging
import os
import tempfile
from unittest.mock import MagicMock, patch

import numpy
import pytest

from ska_sdp_wflow_pointing_offset import compute_offset, construct_antennas

log = logging.getLogger("pointing-offset-logger")
log.setLevel(logging.WARNING)

default_run = True
persist = False
NTIMES = 4
NANTS = 6
NCHAN = 5
XYZ = numpy.array(
    [
        [5109237.714735, 2006795.661955, -3239109.183708],
        [5109251.156928, 2006811.008353, -3239078.678007],
    ]
)
DIAMETER = numpy.array([13.5, 13.5])
STATION = ["M000", "M001"]


class MockRDBInput:
    """
    Mock RDB Input Class
    """

    def timestamps(self):
        return numpy.linspace(1, 10, 9)

    def target_projection(self):
        return "ARC"

    def ants(self):
        return construct_antennas(XYZ, DIAMETER, STATION)

    def target_x(self):
        return numpy.array(
            [
                [-1.67656219e-05, -3.86416795e-05, 2.54736615e-05],
                [1.07554380e-04, 1.27813267e-04, -2.93635031e-05],
                [-4.95111837e-04, 1.35920940e-04, -3.10228964e-04],
                [4.41771802e-04, -2.76304939e-04, 7.46971279e-05],
                [1.19623691e-04, -2.71621773e-05, -3.05732096e-04],
            ]
        )

    def target_y(self):
        return numpy.array(
            [
                [-1.00010232e00, -1.00007682e00, -9.99948506e-01],
                [-1.00002945e00, -1.00019367e00, -1.00028369e00],
                [-3.33403243e-01, -3.33692559e-01, -3.33309663e-01],
                [-3.33445411e-01, -3.33362257e-01, -3.33419971e-01],
                [3.33257413e-01, 3.33446516e-01, 3.32922029e-01],
            ]
        )


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
    assert len(read_out) == NANTS
    # other assertions

    # clean up directory
    if persist is False:
        try:
            os.remove(tempdir + "/pointing_offsets.txt")
        except OSError:
            pass
