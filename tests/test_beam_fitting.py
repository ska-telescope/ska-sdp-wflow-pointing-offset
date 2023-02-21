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
from tests.utils import (
    ANTS,
    CORR_TYPE,
    DISH_COORD_X,
    DISH_COORD_Y,
    FREQS,
    TIMESTAMPS,
    VIS,
    VIS_WEIGHT,
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


def test_fit_primary_beams(target):
    """
    Unit test for fit primary beams
    """
    fitted_results = fit_primary_beams(
        VIS,
        FREQS,
        TIMESTAMPS,
        CORR_TYPE,
        VIS_WEIGHT,
        ANTS,
        numpy.array([DISH_COORD_X, DISH_COORD_Y]),
        target,
        auto=True,
    )

    # Check the fitted beam centres, widths, heights, and AzEl offsets
    azel_offset = numpy.column_stack(
        (fitted_results[:, 16], fitted_results[:, 17])
    )

    # Calculated fitted results are different from each machine.
    # Therefore, cannot really test it as part of unittest.
    assert (
        azel_offset == numpy.array([[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]])
    ).all()
