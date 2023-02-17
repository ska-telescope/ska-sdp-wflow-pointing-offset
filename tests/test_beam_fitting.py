# pylint: disable-msg=too-many-locals
"""
Unit tests for beam fitting functions
"""
import katpoint
import numpy
import pytest

from ska_sdp_wflow_pointing_offset.coord_support import construct_antennas
from src.ska_sdp_wflow_pointing_offset.beam_fitting import (
    _fwhm_to_sigma,
    _sigma_to_fwhm,
    fit_primary_beams,
)

# Define the parameters for fit primary beam function
CORR_TYPE = ["XX", "YY"]
TIMESTAMPS = numpy.array(
    [
        1.67272797e09,
        1.67272798e09,
        1.67272800e09,
        1.67272801e09,
        1.67272803e09,
    ]
)
FREQS = numpy.array(
    [
        8.56000000e08,
        8.56208984e08,
        8.56417969e08,
        8.56626953e08,
        8.56835938e08,
    ]
)

# Visibility - the y parameter to be used in the fitting
VIS = numpy.array(
    [
        [
            10431.873,
            9127.823,
            10141.914,
            59011.547,
            10860.39,
            9806.72,
            9204.591,
            17989.33,
            30690.541,
            14414.348,
            15283.417,
            14005.097,
            9860.686,
            26317.227,
            9236.236,
        ],
        [
            10431.873,
            9127.823,
            10141.914,
            59011.547,
            10860.39,
            9806.72,
            9204.591,
            17989.33,
            30690.541,
            14414.348,
            15283.417,
            14005.097,
            9860.686,
            26317.227,
            9236.236,
        ],
    ]
)

# Weights - used as standard deviation on the y-parameter
VIS_WEIGHT = numpy.array(
    [
        [
            0.16797385,
            0.17385559,
            0.16107331,
            0.19380789,
            0.11699289,
            0.1938036,
            0.17419179,
            0.18623605,
            0.16278373,
            0.15633371,
            0.17856638,
            0.18040745,
            0.15366295,
            0.15283653,
            0.16469233,
        ],
        [
            0.15729496,
            0.16163893,
            0.16258055,
            0.1790921,
            0.11462438,
            0.19291812,
            0.1803138,
            0.17485328,
            0.17238507,
            0.1655575,
            0.17291346,
            0.18430558,
            0.17445499,
            0.10147141,
            0.13969643,
        ],
    ]
)


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
    beam_centre = numpy.column_stack(
        (fitted_results[:, 0], fitted_results[:, 1])
    )
    beam_width = numpy.column_stack(
        (fitted_results[:, 4], fitted_results[:, 5])
    )
    beam_height = numpy.column_stack(
        (fitted_results[:, 8], fitted_results[:, 9])
    )
    azel_offset = numpy.column_stack(
        (fitted_results[:, 16], fitted_results[:, 17])
    )

    assert (
        beam_centre
        == numpy.array(
            [
                [4.6571771692076765e37, -29.09686712644969],
                [-6.096692901691223e65, -3838.2847294497396],
                [-6.096692901691223e65, -3838.2847294497396],
            ]
        )
    ).all()
    assert (
        beam_width
        == numpy.array(
            [
                [3.669547123871928e50, 10.382954619419637],
                [2.9127664262544846e78, 711.0432883762637],
                [2.9127664262544846e78, 711.0432883762637],
            ]
        )
    ).all()
    assert (
        beam_height
        == numpy.array(
            [
                [23583982785955.715, 23583982785955.715],
                [2.091837530042313e16, 2.091837530042313e16],
                [2.091837530042313e16, 2.091837530042313e16],
            ]
        )
    ).all()
    assert (
        azel_offset == numpy.array([[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]])
    ).all()
