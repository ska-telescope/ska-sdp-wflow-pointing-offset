# pylint:disable=too-many-function-args
"""
Unit tests for frequency selection functions
"""
from unittest.mock import patch

import numpy

from ska_sdp_wflow_pointing_offset.array_data_func import (
    apply_rfi_mask,
    interp_timestamps,
    select_channels,
)
from tests.utils import DISH_COORD_AZ, DISH_COORD_EL, TIMESTAMPS

NCHAN = 5
FREQS = numpy.linspace(1.0e8, 3.0e8, NCHAN)


@patch("numpy.loadtxt")
def test_apply_rfi_mask(mock_load):
    """
    Unit test for apply_rfi_mask
    Assume same length for RFI mask and visibility frequency
    """
    mock_load.return_value = numpy.array([1, 1, 0, 1, 1])
    result_freqs, result_channels = apply_rfi_mask(
        FREQS, rfi_filename="fake_file"
    )

    assert result_freqs == numpy.array([2.0e8])
    assert result_channels == numpy.array([2])


def test_apply_rfi_mask_wrong_file():
    """
    Unit test for apply_rfi_mask
    If wrong file name is provided
    """
    result_freqs, result_channels = apply_rfi_mask(
        FREQS, rfi_filename="fake_file"
    )

    assert (result_freqs == FREQS).all()
    assert (result_channels == numpy.array(range(NCHAN))).all()


def test_select_channels():
    """
    Unit test for select_channels
    """

    result_freqs, result_channels = select_channels(
        FREQS, numpy.array(range(NCHAN)), 1.8e8, 2.8e8
    )
    assert result_freqs.all() == numpy.array([2.0e8, 2.5e8]).all()
    assert result_channels.all() == numpy.array([2, 3]).all()


def test_interp_timestamps():
    """
    Unit test for interp_timestamps
    """
    dish_coord = numpy.dstack([DISH_COORD_AZ, DISH_COORD_EL])
    offset = dish_coord.reshape(5, 3, 2)

    # If the interpolated ntimes is larger than original
    long_timestamps = numpy.linspace(TIMESTAMPS[0], TIMESTAMPS[-1], 10)
    out = interp_timestamps(offset, TIMESTAMPS, long_timestamps)

    assert out.shape == (10, 3, 2)
    # The start and end should be the same
    numpy.testing.assert_array_almost_equal(out[0], offset[0])
    numpy.testing.assert_array_almost_equal(out[-1], offset[-1])

    # If the interpolated ntimes is less than original
    short_timestamps = numpy.linspace(TIMESTAMPS[1], TIMESTAMPS[-2], 4)
    out = interp_timestamps(offset, TIMESTAMPS, short_timestamps)
    assert out.shape == (4, 3, 2)
    numpy.testing.assert_array_almost_equal(out[0], offset[1])
    numpy.testing.assert_array_almost_equal(out[-1], offset[-2])
