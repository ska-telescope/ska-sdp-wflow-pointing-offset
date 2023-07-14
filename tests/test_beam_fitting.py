# pylint: disable=too-many-arguments
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


def test_fit_to_visibilities(
    y_per_scan_vis, x_per_scan, frequency, ants, target, pointing_timestamps
):
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
    pointing_offset = weighted_average(
        ants, fitted_beams, target, pointing_timestamps, 1
    )

    # Check the antenna names, AzEl and Cross-El offset
    assert (
        pointing_offset[:, 0] == numpy.array(["M001", "M002", "M003"])
    ).all()
    assert (numpy.isnan(pointing_offset[:, 1].astype(float))).all()
    assert (numpy.isnan(pointing_offset[:, 2].astype(float))).all()
    assert (numpy.isnan(pointing_offset[:, 3].astype(float))).all()


def test_fit_to_gain(
    y_per_scan_gains,
    x_per_scan,
    frequency_per_chunk,
    ants,
    weights_per_scan,
    target,
    pointing_timestamps,
):
    """
    Unit test for fitting primary beams to gain amplitudes
    """
    fitted_beams = SolveForOffsets(
        x_per_scan,
        y_per_scan_gains,
        frequency_per_chunk,
        BEAMWIDTH_FACTOR,
        ants,
        THRESH_WIDTH,
    ).fit_to_gains(weights_per_scan, 16)

    # Check the fitted AzEl offsets
    pointing_offset = weighted_average(
        ants, fitted_beams, target, pointing_timestamps, 16
    )

    # Check the antenna names, Az offset, El offset and Cross-El offset
    assert (
        pointing_offset[:, 0] == numpy.array(["M001", "M002", "M003"])
    ).all()
    numpy.testing.assert_almost_equal(
        pointing_offset[:, 1].astype(float),
        numpy.array([-0.534807, -1.496948, -1.615558]),
        decimal=6,
    )
    numpy.testing.assert_almost_equal(
        pointing_offset[:, 2].astype(float),
        numpy.array([-0.776804, -0.816107, -0.90116]),
        decimal=6,
    )
    numpy.testing.assert_almost_equal(
        pointing_offset[:, 3].astype(float),
        numpy.array([-0.435635, -1.219365, -1.315978]),
        decimal=6,
    )
