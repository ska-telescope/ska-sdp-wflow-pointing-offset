"""
Unit tests for workflow functions
"""
import logging
import pytest
import numpy as np

from unittest.mock import patch, Mock

from ska_sdp_wflow_pointing_offset.workflow import(
    apply_rfi_mask,
    select_channels,
    clean_vis_data,
)

log = logging.getLogger("pointing-logger")
log.setLevel(logging.INFO)

@pytest.fixture(scope="module", name="input_params")
def input_fixture():

    nants = 6
    nchan = 5
    npol = 2
    freqs = np.linspace(1.e8, 3.e8, nchan)
    vis = np.ones((nants, nchan, npol))
    vis = np.add(vis, np.array([1, 2, 3, 4, 5]), axis=1)

    corr_type=['XX' 'YY']

    params = {
        "visibility": vis,
        "frequency": freqs,
        "corr_type": corr_type,
    }
    return params

#still working on this
@patch("rfi_mask", Mock(return_value=np.array([1,1,0,1,1]))
def test_apply_rfi_mask(input_params):
    """
    Unit test for apply_rfi_mask
    """
    vis = input_params["visibility"]
    freqs = input_params["frequency"]
    result_vis, result_freqs = apply_rfi_mask(vis,freqs, rfi_name='fake_file')

    assert result_vis.shape == (6,1,2)
    assert result_freqs == np.array([2.e8])


def test_select_channels(input_params):
    """
    Unit test for select_channels
    """
    vis = input_params["visibility"]
    freqs = input_params["frequency"]
    result_vis, result_freq = select_channels(vis, freqs, 1.8e8, 2.8e8)
    assert result_vis.shape == (6, 2, 2)
    assert result_freq.shape == 2
    assert result_vis[0, 0, 0] == 4

def test_clean_vis_data(input_params):
    """
    Unit test for clean_vis_data
    """

    vis = input_params["visibility"]
    freqs = input_params["frequency"]
    corr_type = input_params["corr_type"]

    hh, vv = clean_vis_data(vis, freqs, corr_type, split_pol=True)

    assert (hh[:] == 4.0).all()
    assert (vv[:] == 4.0).all()

