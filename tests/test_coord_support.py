"""
Unit test for coordinate support functions.
"""

import katpoint
import numpy

from ska_sdp_wflow_pointing_offset.coord_support import (
    construct_antennas,
    convert_coordinates,
)

# Assume 2 antennas
XYZ = numpy.array(
    [
        [5109237.714735, 2006795.661955, -3239109.183708],
        [5109251.156928, 2006811.008353, -3239078.678007],
    ]
)
DIAMETER = numpy.array([13.5, 13.5])
STATION = ["M000", "M001"]


def test_construct_antennas():
    """
    Unit test for construct antennas
    """

    ants = construct_antennas(XYZ, DIAMETER, STATION)
    assert len(ants) == 2
    assert ants[0].name == "M000"
    assert ants[0].diameter == 13.5


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
    ants = construct_antennas(XYZ, DIAMETER, STATION)
    fitted_az = numpy.zeros(len(ants))
    fitted_el = numpy.zeros(len(ants))
    for i, antenna in enumerate(ants):
        fitted_az[i], fitted_el[i] = convert_coordinates(
            antenna,
            beam_centre,
            timestamps,
            target_projection,
            target,
        )

    assert fitted_az.all() == numpy.array([2.32326059, 2.32326058]).all()
    assert fitted_el.all() == numpy.array([0.6999862, 0.69998617]).all()
