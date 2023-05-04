"""
Unit tests for frequency selection functions
"""
from unittest.mock import MagicMock, patch

import numpy

from ska_sdp_wflow_pointing_offset.freq_select import (
    apply_rfi_mask,
    select_channels,
    interp_timestamps,
)
from tests.utils import SOURCE_OFFSET_X, SOURCE_OFFSET_Y

NCORR = 15
NCHAN = 5
NPOL = 2
FREQS = numpy.linspace(1.0e8, 3.0e8, NCHAN)
VIS = numpy.ones((NCORR, NCHAN, NPOL))
CORR_TYPE = ["XX", "YY"]
VIS_WEIGHT = numpy.ones((NCORR, NPOL))


@patch("builtins.open", MagicMock())
@patch("numpy.loadtxt")
def test_apply_rfi_mask(mock_load):
    """
    Unit test for apply_rfi_mask
    Assume same length for RFI mask and visibility frequency
    """
    mock_load.return_value = numpy.array([1, 1, 0, 1, 1])
    result_vis, result_freqs = apply_rfi_mask(
        VIS, FREQS, rfi_filename="fake_file"
    )

    assert result_vis.shape == (15, 1, 2)
    assert result_freqs == numpy.array([2.0e8])


def test_apply_rfi_mask_wrong_file():
    """
    Unit test for apply_rfi_mask
    If wrong file name is provided
    """
    result_vis, result_freqs = apply_rfi_mask(
        VIS, FREQS, rfi_filename="fake_file"
    )

    assert (result_vis == VIS).all()
    assert (result_freqs == FREQS).all()


@patch("builtins.open", MagicMock())
@patch("numpy.loadtxt")
def test_apply_rfi_mask_short_mask(mock_load):
    """
    Unit test when the RFI mask has fewer channels
    than Visibility frequency
    """
    mock_load.return_value = numpy.array([1, 1, 0])
    result_vis, result_freqs = apply_rfi_mask(
        VIS, FREQS, rfi_filename="fake_file"
    )

    assert result_vis.shape == (15, 3, 2)
    assert (result_freqs == numpy.array([2.0e8, 2.5e8, 3.0e8])).all()


@patch("builtins.open", MagicMock())
@patch("numpy.loadtxt")
def test_apply_rfi_mask_long_mask(mock_load):
    """
    Unit test when the RFI mask has more channels
    than Visibility frequency
    """
    mock_load.return_value = numpy.array([1, 1, 0, 1, 1, 0])
    result_vis, result_freqs = apply_rfi_mask(
        VIS, FREQS, rfi_filename="fake_file"
    )

    assert result_vis.shape == (15, 1, 2)
    assert result_freqs == numpy.array([2.0e8])


def test_select_channels():
    """
    Unit test for select_channels
    """

    result_vis, result_freq = select_channels(VIS, FREQS, 1.8e8, 2.8e8)
    assert result_vis.shape == (15, 2, 2)
    assert result_freq.all() == numpy.array([2.0e8, 2.5e8]).all()

def test_interp_timestamps():
    """
    Unit test for interp_timestamps
    """
    offset = numpy.array([SOURCE_OFFSET_X, SOURCE_OFFSET_Y])
    assert offset.shape == (2,5,3)

    out = interp_timestamps(offset, 10)

    assert out.shape == (2,10,3)
    # The start and end should be the same
    numpy.testing.assert_array_almost_equal(out[:,0,:], offset[:,0,:])
    numpy.testing.assert_array_almost_equal(out[:, -1, :], offset[:, -1, :])