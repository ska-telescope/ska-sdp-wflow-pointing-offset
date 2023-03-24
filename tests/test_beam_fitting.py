# pylint: disable-msg=too-many-locals
"""
Unit tests for beam fitting functions
"""
import numpy

from ska_sdp_wflow_pointing_offset.beam_fitting import (
    _fwhm_to_sigma,
    _sigma_to_fwhm,
    fit_primary_beams,
)
from tests.utils import (
    ANTS,
    CORR_TYPE,
    FREQS,
    SOURCE_OFFSET_X,
    SOURCE_OFFSET_Y,
    VIS,
    VIS_WEIGHTS,
)


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


def test_fit_primary_beams():
    """
    Unit test for fit primary beams
    """
    fitted_results = fit_primary_beams(
        VIS,
        FREQS,
        CORR_TYPE,
        VIS_WEIGHTS,
        ANTS,
        numpy.array([SOURCE_OFFSET_X, SOURCE_OFFSET_Y]),
    )

    # For Polarisation 1, assert the AzEl offset for each antenna
    assert numpy.allclose(
        numpy.column_stack((fitted_results[:, 0], fitted_results[:, 1])),
        [[-1.13848967, -1.1102361], [-1.98823527, -2.03476453], [0.0, 0.0]],
    )

    # For Polarisation 2, assert the AzEl offset for each antenna
    assert numpy.allclose(
        numpy.column_stack((fitted_results[:, 11], fitted_results[:, 12])),
        [[-2.66941723, 2.14513271], [0.0, 0.0], [-0.34863202, -1.73848721]],
    )
