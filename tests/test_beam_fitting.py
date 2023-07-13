"""
Unit tests for beam fitting functions
"""
import numpy

from ska_sdp_wflow_pointing_offset.array_data_func import weighted_average
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


def test_fit_to_visibilities(y_per_scan_vis, x_per_scan, frequency, ants):
    """
    Unit test for fitting primary beams to visibility amplitudes
    """
    fitted_beams = SolveForOffsets(
        x_per_scan,
        y_per_scan_vis,
        numpy.mean(frequency),
        BEAMWIDTH_FACTOR,
        ants,
        THRESH_WIDTH,
    ).fit_to_visibilities()
    azel_offset = weighted_average(ants, fitted_beams)
    assert (numpy.isnan(azel_offset[:, 0])).all()
    assert (numpy.isnan(azel_offset[:, 1])).all()


def test_fit_to_gain(
    y_per_scan_gains, x_per_scan, frequency, ants, weights_per_scan
):
    """
    Unit test for fitting primary beams to gain amplitudes
    """
    fitted_beams = SolveForOffsets(
        x_per_scan,
        y_per_scan_gains,
        numpy.mean(frequency),
        BEAMWIDTH_FACTOR,
        ants,
        THRESH_WIDTH,
    ).fit_to_gains(weights_per_scan)

    # Check the fitted AzEl offsets
    azel_offset = weighted_average(ants, fitted_beams)
    numpy.testing.assert_almost_equal(
        azel_offset[:, 0],
        numpy.array([-0.000212, -0.000427, -0.00037]),
        decimal=6,
    )
    numpy.testing.assert_almost_equal(
        azel_offset[:, 1],
        numpy.array([-0.000173, -0.000235, -0.000222]),
        decimal=6,
    )
