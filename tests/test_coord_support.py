"""
Unit test for coordinate support functions.
"""

import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord

from ska_sdp_wflow_pointing_offset.coord_support import (
    construct_antennas,
    convert_coordinates,
)

# Assume 2 antennas
XYZ = np.array(
    [
        [5109237.714735, 2006795.661955, -3239109.183708],
        [5109251.156928, 2006811.008353, -3239078.678007],
    ]
)
DIAMETER = np.array([13.5, 13.5])
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
    target_coord = SkyCoord(
        ra=+180.0 * u.deg,
        dec=-35.0 * u.deg,
        frame="icrs",
        equinox="J2000",
    )
    timestamps = np.linspace(1, 10, 9)
    target_projection = "ARC"
    ants = construct_antennas(XYZ, DIAMETER, STATION)
    result_az, result_el = convert_coordinates(
        ants,
        beam_centre,
        timestamps,
        target_projection,
        target_coord=target_coord,
    )

    assert result_az.all() == np.array([2.32326059, 2.32326058]).all()
    assert result_el.all() == np.array([0.6999862, 0.69998617]).all()
