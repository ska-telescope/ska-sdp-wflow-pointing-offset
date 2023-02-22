"""
Unit test for coordinate support functions.
"""

import katpoint
import numpy

from ska_sdp_wflow_pointing_offset.coord_support import (
    construct_antennas,
    convert_coordinates,
)
from tests.utils import ANTS, DIAMETER, STATION, XYZ


def test_construct_antennas():
    """
    Unit test for construct antennas
    """

    ants = construct_antennas(XYZ, DIAMETER, STATION)
    assert len(ants) == 3
    assert ants[0].name == "SKAMID-CORE"
    assert ants[0].diameter == 25.0


def test_convert_coordinates():
    """
    Unit test for convert_coordinates
    """

    beam_centre = (0.11, 0.54)
    cat = katpoint.Catalogue(
        "J1939-6342, radec, 19:39:25.02671, -63:42:45.6255"
    )
    target = cat.targets[0]
    timestamps = numpy.linspace(1, 10, 9)
    target_projection = "ARC"
    fitted_az = numpy.zeros(len(ANTS))
    fitted_el = numpy.zeros(len(ANTS))
    for i, antenna in enumerate(ANTS):
        fitted_az[i], fitted_el[i] = convert_coordinates(
            antenna,
            beam_centre,
            timestamps,
            target_projection,
            target,
        )

    assert fitted_az.all() == numpy.array([2.32326059, 2.32326058]).all()
    assert fitted_el.all() == numpy.array([0.6999862, 0.69998617]).all()
