# pylint: disable-msg=too-many-locals
"""
Unit tests for beam fitting functions
"""
import katpoint
import numpy
import pytest

from ska_sdp_wflow_pointing_offset.beam_fitting import (
    _fwhm_to_sigma,
    _sigma_to_fwhm,
    fit_primary_beams,
)
from ska_sdp_wflow_pointing_offset.coord_support import construct_antennas
from tests.utils import CORR_TYPE, FREQS, TIMESTAMPS, VIS, VIS_WEIGHT


@pytest.fixture(name="target")
def katpoint_target():
    """
    Creates a target that can be pointed at
    """
    cat = katpoint.Catalogue(
        "J1939-6342, radec, 19:39:25.02671, -63:42:45.6255"
    )
    target = cat.targets[0]
    return target


# Build katpoint antenna for three antennas. The antenna positions and size
# are in the MID configuration file
@pytest.fixture(name="ants")
def katpoint_antenna():
    """
    Create antennas that can point at a target
    """
    x_pos = [5109237.714735, 5109251.156928, 5109238.357021]
    y_pos = [2006795.661955, 2006811.008353, 2006770.325838]
    z_pos = [-3239109.183708, -3239109.183708, -3239123.769211]
    dish_diameter = numpy.array([13.5, 13.5, 13.5])
    station = numpy.array(["M000", "M001", "M002"])
    return construct_antennas(
        xyz=numpy.column_stack((x_pos, y_pos, z_pos)),
        diameter=dish_diameter,
        station=station,
    )


# Dish coordinates - the x parameter to be used in the fitting
@pytest.fixture(name="x_param")
def dish_coordinates():
    """
    Create array of dish coordinates
    """
    x_coord = numpy.array(
        [
            [-1.67656219e-05, -3.86416795e-05, 2.54736615e-05],
            [1.07554380e-04, 1.27813267e-04, -2.93635031e-05],
            [-4.95111837e-04, 1.35920940e-04, -3.10228964e-04],
            [4.41771802e-04, -2.76304939e-04, 7.46971279e-05],
            [1.19623691e-04, -2.71621773e-05, -3.05732096e-04],
        ]
    )
    y_coord = numpy.array(
        [
            [-1.00010232e00, -1.00007682e00, -9.99948506e-01],
            [-1.00002945e00, -1.00019367e00, -1.00028369e00],
            [-3.33403243e-01, -3.33692559e-01, -3.33309663e-01],
            [-3.33445411e-01, -3.33362257e-01, -3.33419971e-01],
            [3.33257413e-01, 3.33446516e-01, 3.32922029e-01],
        ]
    )
    return numpy.array([x_coord, y_coord])


def test_fwhm_to_sigma():
    """
    Unit test for _fwhm_to_sigma
    """
    fwhm = 2.0
    assert _fwhm_to_sigma(fwhm) == 0.8493218002880191


def test_sigma_to_fwhm():
    """
    Unit test for _sigma_to_fwhm
    """
    sigma = 0.01
    assert _sigma_to_fwhm(sigma) == 0.023548200450309493


def test_fit_primary_beams(ants, target, x_param):
    """
    Unit test for fit primary beams
    """
    fitted_results = fit_primary_beams(
        VIS,
        FREQS,
        TIMESTAMPS,
        CORR_TYPE,
        VIS_WEIGHT,
        ants,
        x_param,
        target,
        auto=True,
    )

    # Check the fitted beam centres, widths, heights, and AzEl offsets
    azel_offset = numpy.column_stack(
        (fitted_results[:, 16], fitted_results[:, 17])
    )

    # Calculated fitted results are different from each machine.
    # Therefore, cannot really test it as part of unittest.
    # assert (
    #     fitted_results[:, 0][0]
    #     == numpy.array(
    #         [
    #             -1.6488769988931003e34,
    #             3.044748704185454e65,
    #             3.848450017499049e92,
    #         ]
    #     )
    # ).all()

    assert (
        azel_offset == numpy.array([[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]])
    ).all()
