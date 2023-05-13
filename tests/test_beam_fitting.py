"""
Unit tests for beam fitting functions
"""
import numpy

from ska_sdp_wflow_pointing_offset.beam_fitting import (
    SolveForOffsets,
    _fwhm_to_sigma,
    _sigma_to_fwhm,
)
from tests.utils import BEAMWIDTH_FACTOR, FITTING_THRESH


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
        FITTING_THRESH,
    )
    fitted_results = initial_fit.fit_to_visibilities()

    # For Polarisation 1, assert the AzEl offset for each antenna
    az_offset_pol1 = fitted_results[:, 0]
    el_offset_pol1 = fitted_results[:, 1]
    cross_el_offset_pol1 = fitted_results[:, 4]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol1, el_offset_pol1)),
        [[-0.68159, -0.353595], [1.859431, -1.650717], [0.09855, -0.397562]],
        rtol=1e-3,
    )
    numpy.testing.assert_allclose(
        cross_el_offset_pol1, [-32.223557, 12.006591, 4.616732], rtol=1e-3
    )

    # For Polarisation 2, assert the AzEl offset for each antenna
    az_offset_pol2 = fitted_results[:, 11]
    el_offset_pol2 = fitted_results[:, 12]
    cross_el_offset_pol2 = fitted_results[:, 16]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol2, el_offset_pol2)),
        [
            [0.141424, -1.919972],
            [0.141422, -2.201798],
            [0.14278, 2.111914],
        ],
        rtol=1e-3,
    )
    numpy.testing.assert_allclose(
        cross_el_offset_pol2, [-90.770529, -104.076314, 98.970986], rtol=1e-3
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
        FITTING_THRESH,
    )
    fitted_results = initial_fit.fit_to_gains()

    # For Polarisation 1, assert the AzEl and cross-el
    # offsets for each antenna
    az_offset_pol1 = fitted_results[:, 0]
    el_offset_pol1 = fitted_results[:, 1]
    cross_el_offset_pol1 = fitted_results[:, 4]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol1, el_offset_pol1)),
        [[1.779095, -2.685431], [0.0, 0.0], [0.0, 0.0]],
        rtol=1e-3,
    )
    numpy.testing.assert_allclose(
        cross_el_offset_pol1, [84.110311, 0.0, 0.0], rtol=1e-3
    )

    # For Polarisation 2, assert the AzEl and cross-el
    # offsets for each antenna
    az_offset_pol2 = fitted_results[:, 11]
    el_offset_pol2 = fitted_results[:, 12]
    cross_el_offset_pol2 = fitted_results[:, 16]
    numpy.testing.assert_allclose(
        numpy.column_stack((az_offset_pol2, el_offset_pol2)),
        [[5.167355e09, 0.0], [0.0, -5.391624e-01], [0.0, 0.0]],
        rtol=1e-3,
    )
    numpy.testing.assert_allclose(
        cross_el_offset_pol2, [0.0, -25.485551, 0.0], rtol=1e-3
    )
