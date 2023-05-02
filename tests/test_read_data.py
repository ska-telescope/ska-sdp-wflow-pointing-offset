"""
Unit Tests to read data
from CASA Measurement Tables
"""
from unittest.mock import patch

import numpy

from tests.utils import (
    ANTS,
    CORR_TYPE,
    DISH_COORD_AZ,
    DISH_COORD_EL,
    FREQS,
    VIS_ARRAY,
)


@patch("ska_sdp_wflow_pointing_offset.read_data.read_visibilities")
def test_read_visibilities(mock_tables):
    """
    Test importing gaintable from cal table
    """
    mock_tables.return_value = (
        VIS_ARRAY,
        numpy.dstack((DISH_COORD_AZ, DISH_COORD_EL)),
        ANTS,
    )

    vis = mock_tables.return_value[0]
    source_offset = mock_tables.return_value[1]
    ants = mock_tables.return_value[2]

    # Specific attributes
    assert vis.vis.data.shape == (5, 6, 5, 2)
    assert vis.weight.data.shape == (5, 6, 5, 2)
    assert (vis.frequency.data == FREQS).all()
    assert (vis.polarisation.data == CORR_TYPE).all()
    assert source_offset.shape == (5, 3, 2)
    assert numpy.array(ants).shape == (3,)
    assert ants[0].name == "SKAMID-CORE"
    assert ants[0].diameter == 25.0
