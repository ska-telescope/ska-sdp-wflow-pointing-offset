"""
Unit tests for workflow functions
"""
import logging
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from ska_sdp_wflow_pointing_offset.workflow import (
    apply_rfi_mask,
    clean_vis_data,
    select_channels,
)

log = logging.getLogger("pointing-logger")
log.setLevel(logging.INFO)


@pytest.fixture(scope="module", name="input_params")
def input_fixture():
    """
    Input parameters
    """
    nants = 6
    nchan = 5
    npol = 2
    freqs = np.linspace(1.0e8, 3.0e8, nchan)
    vis = np.ones((nants, nchan, npol))
    corr_type = ["XX", "YY"]

    params = {
        "visibility": vis,
        "frequency": freqs,
        "corr_type": corr_type,
    }
    return params


@patch("builtins.open", MagicMock())
@patch("pickle.load")
def test_apply_rfi_mask(mock_load, input_params):
    """
    Unit test for apply_rfi_mask
    """
    vis = input_params["visibility"]
    freqs = input_params["frequency"]
    mock_load.return_value = np.array([1, 1, 0, 1, 1])
    result_vis, result_freqs = apply_rfi_mask(vis, freqs, rfi_name="fake_file")

    assert result_vis.shape == (6, 1, 2)
    assert result_freqs == np.array([2.0e8])


def test_select_channels(input_params):
    """
    Unit test for select_channels
    """
    vis = input_params["visibility"]
    freqs = input_params["frequency"]
    result_vis, result_freq = select_channels(vis, freqs, 1.8e8, 2.8e8)
    assert result_vis.shape == (6, 2, 2)
    assert result_freq.shape == (2,)


def test_clean_vis_data(input_params):
    """
    Unit test for clean_vis_data
    """

    vis = input_params["visibility"]
    freqs = input_params["frequency"]
    corr_type = input_params["corr_type"]

    pol1, pol2 = clean_vis_data(vis, freqs, corr_type, split_pol=True)

    assert pol1.shape == (6,)
    assert np.sum(pol2) == 6
