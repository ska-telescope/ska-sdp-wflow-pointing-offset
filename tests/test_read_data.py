"""
Unit Tests to read data
from CASA Measurement Tables
"""
from unittest.mock import patch

import numpy
import pytest

from ska_sdp_wflow_pointing_offset.read_data import (
    read_batch_visibilities,
    read_visibilities,
)
from tests.utils import (
    CORR_TYPE,
    FREQS,
    MockPointingTable,
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
    )
    mock_ms.return_value = [vis_array]
    vis, source_offset, actual_pointing_el, ants = read_batch_visibilities(
        mock_dir
    )

    # Specific attributes
    assert vis.vis.data.shape == (5, 6, 5, 2)
    assert vis.weight.data.shape == (5, 6, 5, 2)
    assert (vis.frequency.data == FREQS).all()
    assert (vis.polarisation.data == CORR_TYPE).all()
    assert source_offset.shape == (5, 3, 2)
    assert actual_pointing_el.shape == (5, 3)
    assert numpy.array(ants).shape == (3,)
    assert ants[0].name == "SKA001"
    assert ants[0].diameter == 25.0
