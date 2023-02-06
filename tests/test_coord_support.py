"""
Unit test for coordinate support functions.
"""

import astropy.units as u
import numpy as np
import pytest
from astropy.coordinates import SkyCoord

from ska_sdp_wflow_pointing_offset.coord_support import (
    construct_antennas,
    convert_coordinates,
)


@pytest.fixture(scope="module", name="input_params")
def input_fixture():
    """
    Input parameters
    """
    # Assume 2 antennas
    xyz = np.array(
        [
            [5109237.714735, 2006795.661955, -3239109.183708],
            [5109251.156928, 2006811.008353, -3239078.678007],
        ]
    )
    diameter = np.array([13.5, 13.5])
    station = ["M000", "M001"]

    params = {
        "xyz": xyz,
        "diameter": diameter,
        "station": station,
    }
    return params


def test_construct_antennas(input_params):
    """
    Unit test for construct antennas
    """
    xyz = input_params["xyz"]
    diameter = input_params["diameter"]
    station = input_params["station"]
    ants = construct_antennas(xyz, diameter, station)
    assert len(ants) == 2
    assert ants[0].name == "M000"
    assert ants[0].diameter == 13.5


def test_convert_coordinates(input_params):
    """
    Unit test for convert_coordinates
    """
    xyz = input_params["xyz"]
    diameter = input_params["diameter"]
    station = input_params["station"]
    beam_centre = (0.11, 0.54)
    target_coord = SkyCoord(
        ra=+180.0 * u.deg,
        dec=-35.0 * u.deg,
        frame="icrs",
        equinox="J2000",
    )
    timestamps = np.ones((10))
    target_projection = "ARC"
    ants = construct_antennas(xyz, diameter, station)
    result_az, result_el = convert_coordinates(
        ants,
        beam_centre,
        timestamps,
        target_projection,
        target_coord=target_coord,
    )

    assert result_az.all() == np.array([2.32326059, 2.32326058]).all()
    assert result_el.all() == np.array([0.6999862, 0.69998617]).all()
