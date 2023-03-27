# pylint: disable=inconsistent-return-statements,too-few-public-methods
# pylint: disable=duplicate-code
"""
Unit Tests to read data
from CASA Measurement Tables
"""
from unittest.mock import patch

import numpy
import pytest

from ska_sdp_wflow_pointing_offset.read_data import read_visibilities
from tests.utils import (
    FREQS,
    VIS_WEIGHTS,
    MockAntennaTable,
    MockBaseTable,
    MockPointingTable,
    MockPolarisationTable,
    MockSpectralWindowTable,
)

casacore = pytest.importorskip("casacore")


@patch("ska_sdp_wflow_pointing_offset.read_data._load_ms_tables")
def test_read_visibilities(mock_tables):
    """
    Test importing gaintable from cal table
    """
    mock_tables.return_value = (
        MockAntennaTable(),
        MockBaseTable(),
        MockPointingTable(),
        MockPolarisationTable(),
        MockSpectralWindowTable(),
    )
    (
        vis,
        freqs,
        source_offsets,
        vis_weights,
        corr_type,
        ants,
    ) = read_visibilities("test_table")
    assert isinstance(vis, numpy.ndarray)
    assert isinstance(freqs, numpy.ndarray)

    # Specific attributes
    assert vis.shape == (15, 5, 2)
    assert (freqs == FREQS).all()
    assert source_offsets.shape == (2, 5, 3)
    assert vis_weights.shape == (15, 2)
    assert (
        vis_weights.reshape(vis_weights.shape[1], vis_weights.shape[0])
        == VIS_WEIGHTS
    ).all()
    assert (corr_type == numpy.array(["XX", "YY"])).all()
    assert numpy.shape(ants) == (3,)
    assert ants[0].diameter == 25.0
