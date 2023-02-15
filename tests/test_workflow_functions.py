"""
Unit tests for workflow functions
"""
from unittest.mock import MagicMock, patch

import numpy

from ska_sdp_wflow_pointing_offset.workflow import (
    apply_rfi_mask,
    clean_vis_data,
    select_channels,
)

NCORR = 6
NCHAN = 5
NPOL = 2
FREQS = numpy.linspace(1.0e8, 3.0e8, NCHAN)
VIS = numpy.ones((NCORR, NCHAN, NPOL))
CORR_TYPE = ["XX", "YY"]
VIS_WEIGHT = numpy.ones((NCORR, NPOL))


@patch("builtins.open", MagicMock())
@patch("pickle.load")
def test_apply_rfi_mask(mock_load):
    """
    Unit test for apply_rfi_mask
    """
    mock_load.return_value = numpy.array([1, 1, 0, 1, 1])
    result_vis, result_freqs = apply_rfi_mask(
        VIS, FREQS, rfi_filename="fake_file"
    )

    assert result_vis.shape == (6, 1, 2)
    assert result_freqs == numpy.array([2.0e8])


def test_select_channels():
    """
    Unit test for select_channels
    """

    result_vis, result_freq = select_channels(VIS, FREQS, 1.8e8, 2.8e8)
    assert result_vis.shape == (6, 2, 2)
    assert result_freq.all() == numpy.array([2.0e8, 2.5e8]).all()


def test_clean_vis_data():
    """
    Unit test for clean_vis_data
    """

    vis_pols, selected_freq, weight, corr_type = clean_vis_data(
        VIS, FREQS, CORR_TYPE, VIS_WEIGHT
    )

    # The outputs have different sizes
    assert numpy.array(vis_pols).shape == (2, 6)
    assert numpy.sum(numpy.array(vis_pols)) == 12
    assert (
        selected_freq == numpy.array([1.0e08, 1.5e08, 2.0e08, 2.5e08, 3.0e08])
    ).all()
    assert numpy.array(weight).shape == (2, 6)
    assert (corr_type == numpy.array(["XX", "YY"])).all()
