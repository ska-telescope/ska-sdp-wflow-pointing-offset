"""
Fits primary beams to the cross-correlation visibility amplitudes and computes the true
position of the calibrator for computing the azimuth and elevation offsets. This follows
the routines used by the SARAO team for the MeerKAT array. 
"""

import numpy as np
from scikits.fitting import GaussianFit, ScatterFit


def fwhm_to_sigma(fwhm):
    """Standard deviation of Gaussian function with specified FWHM beamwidth.
    This returns the standard deviation of a Gaussian beam pattern with a
    specified full-width half-maximum (FWHM) beamwidth. This beamwidth is the
    width between the two points left and right of the peak where the Gaussian
    function attains half its maximum value.
    """
    # Gaussian function reaches half its peak value at sqrt(2 log 2)*sigma
    return fwhm / 2.0 / np.sqrt(2.0 * np.log(2.0))


def sigma_to_fwhm(sigma):
    """FWHM beamwidth of Gaussian function with specified standard deviation.
    This returns the full-width half-maximum (FWHM) beamwidth of a Gaussian beam
    pattern with a specified standard deviation. This beamwidth is the width
    between the two points left and right of the peak where the Gaussian
    function attains half its maximum value.
    """
    # Gaussian function reaches half its peak value at sqrt(2 log 2)*sigma
    return 2.0 * np.sqrt(2.0 * np.log(2.0)) * sigma
