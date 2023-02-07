"""
Unit tests for workflow functions
"""
from unittest.mock import MagicMock, patch

import numpy as np

from ska_sdp_wflow_pointing_offset.workflow import (
    apply_rfi_mask,
    clean_vis_data,
    select_channels,
)

NCORR = 6
NCHAN = 5
NPOL = 2
FREQS = np.linspace(1.0e8, 3.0e8, NCHAN)
VIS = np.ones((NCORR, NCHAN, NPOL))
CORR_TYPE = ["XX", "YY"]


@patch("builtins.open", MagicMock())
@patch("pickle.load")
def test_apply_rfi_mask(mock_load):
    """
    Unit test for apply_rfi_mask
    """
    mock_load.return_value = np.array([1, 1, 0, 1, 1])
    result_vis, result_freqs = apply_rfi_mask(VIS, FREQS, rfi_name="fake_file")

    assert result_vis.shape == (6, 1, 2)
    assert result_freqs == np.array([2.0e8])


def test_select_channels():
    """
    Unit test for select_channels
    """

    result_vis, result_freq = select_channels(VIS, FREQS, 1.8e8, 2.8e8)
    assert result_vis.shape == (6, 2, 2)
    assert result_freq.all() == np.array([2.0e8, 2.5e8]).all()


def test_clean_vis_data():
    """
    Unit test for clean_vis_data
    """

    pol1, pol2 = clean_vis_data(VIS, FREQS, CORR_TYPE, split_pol=True)

    # The output should be a 1D array of size [Number of cross-correlations]
    assert pol1.shape == (6,)
    assert np.sum(pol2) == 6
