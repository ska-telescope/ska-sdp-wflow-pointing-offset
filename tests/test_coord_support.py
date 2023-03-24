"""
Unit test for coordinate support functions.
"""

from ska_sdp_wflow_pointing_offset.coord_support import construct_antennas
from tests.utils import DIAMETER, STATION, XYZ


def test_construct_antennas():
    """
    Unit test for construct antennas
    """
    ants = construct_antennas(XYZ, DIAMETER, STATION)
    assert len(ants) == 3
    assert ants[0].name == "SKAMID-CORE"
    assert ants[0].diameter == 25.0
