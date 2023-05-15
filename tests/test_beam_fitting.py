"""
Unit tests for beam fitting functions
"""
import numpy

from ska_sdp_wflow_pointing_offset.beam_fitting import (
    SolveForOffsets,
    _fwhm_to_sigma,
    _sigma_to_fwhm,
)
from tests.utils import BEAMWIDTH_FACTOR, THRESH_WIDTH


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


def test_fit_to_visibilities(
    vis_array, source_offset, actual_pointing_el, ants
):
    """
    Unit test for fitting primary beams to visibility amplitudes
    """
    initial_fit = SolveForOffsets(
        source_offset,
        actual_pointing_el,
        vis_array,
        BEAMWIDTH_FACTOR,
        ants,
        THRESH_WIDTH,
    )
    fitted_results = initial_fit.fit_to_visibilities()

    # For Polarisation 1, assert the AzEl offset for each antenna
    az_offset_pol1 = fitted_results[:, 0]
    el_offset_pol1 = fitted_results[:, 1]
    cross_el_offset_pol1 = fitted_results[:, 4]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol1, el_offset_pol1)),
        [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
        rtol=1e-3,
    )
    numpy.testing.assert_allclose(
        cross_el_offset_pol1, [0.0, 0.0, 0.0], rtol=1e-3
    )

    # For Polarisation 2, assert the AzEl offset for each antenna
    az_offset_pol2 = fitted_results[:, 11]
    el_offset_pol2 = fitted_results[:, 12]
    cross_el_offset_pol2 = fitted_results[:, 16]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol2, el_offset_pol2)),
        [
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
        ],
        rtol=1e-3,
    )
    numpy.testing.assert_allclose(
        cross_el_offset_pol2, [0.0, 0.0, 0.0], rtol=1e-3
    )


def test_fit_to_gain(gain_array, source_offset, actual_pointing_el, ants):
    """
    Unit test for fitting primary beams to gain amplitudes
    """
    initial_fit = SolveForOffsets(
        source_offset,
        actual_pointing_el,
        gain_array,
        BEAMWIDTH_FACTOR,
        ants,
        THRESH_WIDTH,
    )
    fitted_results = initial_fit.fit_to_gains()

    # For Polarisation 1, assert the AzEl and cross-el
    # offsets for each antenna
    az_offset_pol1 = fitted_results[:, 0]
    el_offset_pol1 = fitted_results[:, 1]
    cross_el_offset_pol1 = fitted_results[:, 4]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol1, el_offset_pol1)),
        [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
        rtol=1e-3,
    )
    numpy.testing.assert_allclose(
        cross_el_offset_pol1, [0.0, 0.0, 0.0], rtol=1e-3
    )

    # For Polarisation 2, assert the AzEl and cross-el
    # offsets for each antenna
    az_offset_pol2 = fitted_results[:, 11]
    el_offset_pol2 = fitted_results[:, 12]
    cross_el_offset_pol2 = fitted_results[:, 16]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol2, el_offset_pol2)),
        [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
        rtol=1e-3,
    )
    numpy.testing.assert_allclose(
        cross_el_offset_pol2, [0.0, 0.0, 0.0], rtol=1e-3
    )
