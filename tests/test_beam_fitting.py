"""
Unit tests for beam fitting functions
"""
import numpy

from ska_sdp_wflow_pointing_offset.beam_fitting import (
    SolveForOffsets,
    _fwhm_to_sigma,
    _sigma_to_fwhm,
)
from tests.utils import (
    ANTS,
    BEAMWIDTH_FACTOR,
    DISH_COORD_AZ,
    DISH_COORD_EL,
    GAIN_ARRAY,
    VIS_ARRAY,
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


def test_fit_to_visibilities():
    """
    Unit test for fitting primary beams to visibility amplitudes
    """
    initial_fit = SolveForOffsets(
        numpy.dstack((DISH_COORD_AZ, DISH_COORD_EL)),
        VIS_ARRAY,
        BEAMWIDTH_FACTOR,
        ANTS,
    )
    fitted_results = initial_fit.fit_to_visibilities()

    # For Polarisation 1, assert the AzEl offset for each antenna
    az_offset_pol1 = fitted_results[:, 0]
    el_offset_pol1 = fitted_results[:, 1]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol1, el_offset_pol1)),
        [[-1.715361, -0.380931], [-1.053834, 2.103075], [0.415649, -1.845783]],
        rtol=1e-3,
    )

    # For Polarisation 2, assert the AzEl offset for each antenna
    az_offset_pol2 = fitted_results[:, 11]
    el_offset_pol2 = fitted_results[:, 12]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol2, el_offset_pol2)),
        [
            [-0.380931, -1.745447],
            [2.103075, -0.269111],
            [-1.845783, 1.468595],
        ],
        rtol=1e-3,
    )


def test_fit_to_gain():
    """
    Unit test for fitting primary beams to gain amplitudes
    """
    initial_fit = SolveForOffsets(
        numpy.dstack((DISH_COORD_AZ, DISH_COORD_EL)),
        GAIN_ARRAY,
        BEAMWIDTH_FACTOR,
        ANTS,
    )
    fitted_results = initial_fit.fit_to_gains()

    # For Polarisation 1, assert the AzEl offset for each antenna
    az_offset_pol1 = fitted_results[:, 0]
    el_offset_pol1 = fitted_results[:, 1]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol1, el_offset_pol1)),
        [[0.48757, -1.377305], [0.0, 0.0], [0.0, 0.0]],
        rtol=1e-3,
    )

    # For Polarisation 2, assert the AzEl offset for each antenna
    az_offset_pol2 = fitted_results[:, 11]
    el_offset_pol2 = fitted_results[:, 12]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol2, el_offset_pol2)),
        [[0.0, 0.0], [2.865761, 2.939088], [0.0, 0.0]],
        rtol=1e-3,
    )
