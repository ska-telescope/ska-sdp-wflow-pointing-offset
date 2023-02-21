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
    VIS_WEIGHT,
    MockAntennaTable,
    MockBaseTable,
    MockPolarisationTable,
    MockSourceTable,
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
        MockPolarisationTable(),
        MockSpectralWindowTable(),
        MockSourceTable(),
    )
    (
        vis,
        freqs,
        corr_type,
        vis_weight,
        target,
    ) = read_visibilities("test_table")
    assert isinstance(vis, numpy.ndarray)
    assert isinstance(freqs, numpy.ndarray)

    # Specific attributes
    assert vis.shape == (15, 5, 2)
    assert (freqs == FREQS).all()
    assert (corr_type == numpy.array(["XX", "YY"])).all()
    assert vis_weight.shape == (15, 2)
    assert (
        vis_weight.reshape(vis_weight.shape[1], vis_weight.shape[0])
        == VIS_WEIGHT
    ).all()
    assert target.radec() == (5.1461782, -1.11199581)
