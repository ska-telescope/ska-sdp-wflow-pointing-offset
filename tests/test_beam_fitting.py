import pytest
import numpy

from ska_sdp_wflow_pointing_offset.beam_fitting import (
    fit_primary_beams,
    fwhm_to_sigma,
    sigma_to_fwhm,
)
from ska_sdp_wflow_pointing_offset.coord_support import construct_antennas


def test_fwhm_to_sigma():
    """
    Unit test for clean_vis_data
    """
    FWHM = 2.0
    assert fwhm_to_sigma(FWHM) == 0.8493218002880191


def test_sigma_to_fwhm():
    SIGMA = 0.01
    assert sigma_to_fwhm(SIGMA) == 0.023548200450309493


@pytest.fixture(scope="module")
def input_parameters():
    avg_vis = numpy.array(
        [
            [10431.873, 350.10522, 350.10522, 6768.05],
            [9127.823, 348.04205, 348.04205, 6879.5024],
            [10141.914, 379.49243, 379.49243, 6933.978],
        ]
    )
    freqs = numpy.array([8.56000000e08, 8.56208984e08, 8.56417969e08])
    timestamps = numpy.array([1.67272797e09, 1.67272798e09, 1.67272800e09])
    corr_type = ["XX", "YY"]
    vis_weight = numpy.array(
        [
            [0.16797385, 0.16055201, 0.16055201, 0.15729496],
            [0.17385559, 0.16613413, 0.16613413, 0.16163893],
            [0.16107331, 0.16048841, 0.16048841, 0.16258055],
        ]
    )

    # Use katpoint to build antennas
    # Get xyz values from MID configuration file
    # ants = construct_antennas(xyz= ,
    #                          diameter=15.0,
    #                          station=)
    # dish_diameter = ants[0].diameter

    # dish coordinates
    x_coord = numpy.array(
        [
            [-1.67656219e-05, -3.86416795e-05, 2.54736615e-05],
            [1.07554380e-04, 1.27813267e-04, -2.93635031e-05],
            [-4.95111837e-04, 1.35920940e-04, -3.10228964e-04],
        ]
    )

    y_coord = numpy.array(
        [
            [-1.00010232, -1.00007682, -0.99994851],
            [-1.00002945, -1.00019367, -1.00028369],
            [-0.33340324, -0.33369256, -0.33330966],
        ]
    )
    dish_coordinates = numpy.array([x, y])

    # Use katpoint to build target
    # target =

    return (
        avg_vis,
        freqs,
        timestamps,
        corr_type,
        vis_weight,
        ants,
        dish_diameter,
        dish_coordinates,
        target,
    )


def test_fit_primary_beams(input_parameters):
    fit_primary_beams(*input_parameters, save_offset=True)
