# pylint: disable=inconsistent-return-statements,too-few-public-methods
"""
Unit Tests to read data
from CASA Measurement Tables
"""
from unittest.mock import patch

import numpy
import pytest
from conftest import (
    MockAntennaTable,
    MockBaseTable,
    MockPolarisationTable,
    MockSourceTable,
    MockSpectralWindowTable,
)

from ska_sdp_wflow_pointing_offset.read_data import read_visibilities

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
    assert (vis == numpy.array([1, 2, 3, 4, 5, 6, 7, 8, 9])).all()
    assert (freqs == numpy.array([1.0e9, 1.1e9, 1.2e9, 1.3e9, 1.4e9])).all()
    assert (corr_type == numpy.array(["XX", "YY"])).all()
    assert (
        vis_weight
        == numpy.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    ).all()
    assert target.radec() == (5.1461782, -1.11199581)
