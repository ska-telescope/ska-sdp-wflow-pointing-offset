# pylint: disable-msg=too-many-locals
"""
Unit tests for beam fitting functions
"""

import katpoint
import numpy
import pytest

from ska_sdp_wflow_pointing_offset.beam_fitting import (
    fit_primary_beams,
    fwhm_to_sigma,
    sigma_to_fwhm,
)
from ska_sdp_wflow_pointing_offset.coord_support import construct_antennas


def test_fwhm_to_sigma():
    """
    Unit test for fwhm_to_sigma
    """
    fwhm = 2.0
    assert fwhm_to_sigma(fwhm) == 0.8493218002880191


def test_sigma_to_fwhm():
    """
    Unit test for sigma_to_fwhm
    """
    sigma = 0.01
    assert sigma_to_fwhm(sigma) == 0.023548200450309493


@pytest.fixture(scope="module")
def input_parameters():
    """
    Generates input parameters for the beam fitting
    function
    """
    timestamps = numpy.array([1.67272797e9, 1.67272798e9, 1.67272800e9])
    freqs = numpy.array([8.56000000e8, 8.56208984e8, 8.56417969e8])
    cat = katpoint.Catalogue(
        "J1939-6342, radec, 19:39:25.02671, -63:42:45.6255"
    )
    target = cat.targets[0]
    corr_type = ["XX", "YY"]

    # Use katpoint to build antennas using parameters from
    # MID configuration file
    x_pos = [5109237.714735, 5109251.156928, 5109238.357021]
    y_pos = [2006795.661955, 2006811.008353, 2006770.325838]
    z_pos = [-3239109.183708, -3239109.183708, -3239123.769211]
    dish_diameter = numpy.array([13.5, 13.5, 13.5])
    station = numpy.array(["M000", "M001", "M002"])
    ants = construct_antennas(
        xyz=numpy.column_stack((x_pos, y_pos, z_pos)),
        diameter=dish_diameter,
        station=station,
    )

    # Dish coordinates
    x_coord = numpy.array(
        [
            [-1.67656219e-5, -3.86416795e-5, 2.54736615e-5],
            [1.07554380e-4, 1.27813267e-4, -2.93635031e-5],
            [-4.95111837e-4, 1.35920940e-4, -3.10228964e-4],
        ]
    )
    y_coord = numpy.array(
        [
            [-1.00010232, -1.00007682, -0.99994851],
            [-1.00002945, -1.00019367, -1.00028369],
            [-0.33340324, -0.33369256, -0.33330966],
        ]
    )
    dish_coordinates = numpy.array([x_coord, y_coord])

    vis = numpy.array(
        [[2176.092, 2150.038, 2203.6045], [2157.0981, 2169.196, 2137.593]]
    )
    vis_weight = numpy.array(
        [
            [0.16797385, 0.17385559, 0.16107331],
            [0.15729496, 0.16163893, 0.16258055],
        ]
    )

    return (
        vis,
        freqs,
        timestamps,
        corr_type,
        vis_weight,
        ants,
        dish_coordinates,
        target,
    )


def test_fit_primary_beams(input_parameters):
    """
    Unit test for fit primary beams
    """
    # TO DO: Need to test saving results to file
    fit_primary_beams(*input_parameters, save_offset=True)
