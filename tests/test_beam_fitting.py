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
    BEAMWIDTH,
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
        BEAMWIDTH,
    )

    # For Polarisation 1, assert the AzEl offset for each antenna
    az_offset_pol1 = fitted_results[:, 0]
    el_offset_pol1 = fitted_results[:, 1]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol1, el_offset_pol1)),
        [[-1.13939, -1.110319], [-1.988235, -2.034765], [0.0, 0.0]],
        rtol=1e-3,
    )

    # For Polarisation 2, assert the AzEl offset for each antenna
    az_offset_pol2 = fitted_results[:, 11]
    el_offset_pol2 = fitted_results[:, 12]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol2, el_offset_pol2)),
        [[-2.669407, 2.106163], [-1.721364, 2.267566], [0.0, 0.0]],
        rtol=1e-3,
    )
