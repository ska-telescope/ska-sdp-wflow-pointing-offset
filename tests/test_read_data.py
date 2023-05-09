"""
Unit Tests to read data
from CASA Measurement Tables
"""
from unittest.mock import patch

import numpy
import pytest

from ska_sdp_wflow_pointing_offset.read_data import read_visibilities
from tests.utils import (
    CORR_TYPE,
    FREQS,
    VIS_ARRAY,
    MockPointingTable,
    MockSpectralWindowTable,
)

casacore = pytest.importorskip("casacore")


@patch("ska_sdp_datamodels.visibility.create_visibility_from_ms")
@patch("ska_sdp_wflow_pointing_offset.read_data._load_ms_tables")
def test_read_visibilities(mock_tables, mock_ms):
    """
    Unit test for read_visibilities function
    """
    mock_tables.return_value = (
        MockSpectralWindowTable(),
        MockPointingTable(),
    )
    mock_ms.return_value = [VIS_ARRAY]
    vis, source_offset, ants = read_visibilities("fake_ms")

    # Specific attributes
    assert vis.vis.data.shape == (5, 6, 5, 2)
    assert vis.weight.data.shape == (5, 6, 5, 2)
    assert (vis.frequency.data == FREQS).all()
    assert (vis.polarisation.data == CORR_TYPE).all()
    assert source_offset.shape == (5, 3, 2)
    assert numpy.array(ants).shape == (3,)
    assert ants[0].name == "SKAMID-CORE"
    assert ants[0].diameter == 25.0
