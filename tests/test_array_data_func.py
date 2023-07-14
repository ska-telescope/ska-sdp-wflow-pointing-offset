"""
Unit tests for frequency selection functions
"""
from unittest.mock import patch

import numpy

from ska_sdp_wflow_pointing_offset.array_data_func import (
    _compute_gains,
    apply_rfi_mask,
    interp_timestamps,
    select_channels,
)
from tests.utils import (
    POINTING_TIMESTAMPS,
    SOURCE_OFFSET_AZ,
    SOURCE_OFFSET_EL,
    VIS_TIMESTAMPS,
)

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
    offset = numpy.dstack([SOURCE_OFFSET_AZ, SOURCE_OFFSET_EL])
    out = interp_timestamps(offset, POINTING_TIMESTAMPS, VIS_TIMESTAMPS)
    assert out.shape == (5, 3, 2)

    # The start and end should be the same
    numpy.testing.assert_array_almost_equal(out[0], offset[0])
    numpy.testing.assert_array_almost_equal(out[-1], offset[-1])


def test_compute_gains(vis_array):
    """
    Unit test for compute_gains
    """
    gt_list = []
    for vis in vis_array:
        gt_list.append(compute_gains(vis, 1))

    assert len(gt_list) == 5
    assert gt_list[0][0]["gain"].data.shape == (5, 3, 1, 2, 2)
