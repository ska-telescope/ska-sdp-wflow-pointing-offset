"""
Unit Tests to read data
from CASA Measurement Tables
"""
from unittest.mock import patch

import numpy
import pytest

from ska_sdp_wflow_pointing_offset.read_data import read_batch_visibilities
from tests.utils import (
    CORR_TYPE,
    FREQS,
    MockPointingTable,
    MockSourceTable,
    MockSpectralWindowTable,
)

casacore = pytest.importorskip("casacore")


@patch("ska_sdp_wflow_pointing_offset.read_data.create_visibility_from_ms")
@patch("ska_sdp_wflow_pointing_offset.read_data._load_ms_tables")
@patch("glob.glob", return_value=["fake_ms"])
def test_read_batch_visibilities(mock_dir, mock_tables, mock_ms, vis_array):
    """
    Unit test for read_visibilities function
    """
    mock_dir.return_value = ["fake_ms"]
    mock_tables.return_value = (
        MockSpectralWindowTable(),
        MockPointingTable(),
        MockSourceTable(),
    )
    mock_ms.return_value = [vis_array]
    (
        vis,
        source_offset,
        _,
        ants,
        _,
    ) = read_batch_visibilities("test_dir")

    # Specific attributes
    assert vis[0].vis.data.shape == (5, 6, 5, 2)
    assert vis[0].weight.data.shape == (5, 6, 5, 2)
    assert (vis[0].frequency.data == FREQS).all()
    assert (vis[0].polarisation.data == CORR_TYPE).all()
    assert source_offset[0].shape == (5, 3, 2)
    assert numpy.array(ants).shape == (3,)
    assert ants[0].name == "SKA001"
    assert ants[0].diameter == 25.0
