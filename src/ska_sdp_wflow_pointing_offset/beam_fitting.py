# pylint: disable=too-many-instance-attributes,abstract-method
# pylint: disable=too-many-arguments
"""
Fits primary beams modelled by a 2D Gaussian to the visibility
or gain amplitudes and computes the elevation and cross-elevation
offsets. This follows the routines used by the SARAO team for the
MeerKAT array.
"""

import logging

import numpy
from katpoint import lightspeed
from scikits.fitting import GaussianFit, ScatterFit

log = logging.getLogger("ska-sdp-pointing-offset")


def _fwhm_to_sigma(fwhm):
    """
    Standard deviation of Gaussian function with specified
    FWHM beamwidth.

    :param fwhm: Full-width half-maximum (FWHM) beamwidth
    :return: The standard deviation of a Gaussian beam pattern
    with a specified full-width half-maximum (FWHM) beamwidth.
    This beamwidth is the width between the two points left and
    right of the peak where the Gaussian function attains half
    its maximum value
    """
    # Gaussian function reaches half its peak value at sqrt(2 log 2)*sigma
    return fwhm / 2.0 / numpy.sqrt(2.0 * numpy.log(2.0))


def _sigma_to_fwhm(sigma):
    """
    FWHM beamwidth of Gaussian function with specified standard
    deviation.

    :param sigma: The standard deviation of a Gaussian beam pattern
    with a specified full-width half-maximum (FWHM) beamwidth
    :return: The full-width half-maximum (FWHM) beamwidth of a Gaussian
    beam pattern with a specified standard deviation. This beamwidth
    is the width between the two points left and right of the peak
    where the Gaussian function attains half its maximum value
    """
    # Gaussian function reaches half its peak value at sqrt(2 log 2)*sigma
    return 2.0 * numpy.sqrt(2.0 * numpy.log(2.0)) * sigma


class BeamPatternFit(ScatterFit):
    """
    Fit analytic beam pattern to total power data defined on
    2-D plane. This fits a two-dimensional Gaussian curve (with
    diagonal covariance matrix) to total power data as a function
    of 2-D coordinates. The Gaussian bump represents an antenna
    beam pattern convolved with a point source.

    :param centre: Initial guess of 2-element beam centre, in target
        coordinate units
    :param width: Initial guess of single beam width for both dimensions,
        or 2-element beam width vector, expressed as FWHM in units of
        target coordinates
    :param height: Initial guess of beam pattern amplitude or height

    Attributes
    ----------
    expected_width: real array, shape (2,), or float
        Initial guess of beamwidth, saved as expected width for checks
    is_valid : bool
        True if beam parameters are within reasonable ranges after fit
    std_centre: array of float, shape (2,)
        Standard error of beam centre, only set after :func:`fit`
    std_width: array of float, shape (2,), or float
        Standard error of beamwidth(s), only set after :func:`fit`
    std_height: float
        Standard error of beam height, only set after :func:`fit`
    """

    def __init__(self, centre, width, height):
        super().__init__()
        if not numpy.isscalar(width):
            width = numpy.atleast_1d(width)
        self._interp = GaussianFit(centre, _fwhm_to_sigma(width), height)
        self.centre = self._interp.mean
        self.width = _sigma_to_fwhm(self._interp.std)
        self.height = self._interp.height
        self.expected_width = width
        self.is_valid = False
        self.std_centre = self.std_width = self.std_height = None

    def fit(self, x, y, std_y=1.0, thresh_width=1.15):
        """
        Fit a beam pattern to data.
        The centre, width and height of the fitted beam pattern
        (and their standard errors) can be obtained from the
        corresponding member variables after this is run.

        :param x: Sequence of (2, N) target coordinates (as column vectors)
        :param y: Sequence of (N, ) corresponding total power values to fit
        :param std_y: Optional measurement error or uncertainty of (N, ) `y`
            values, expressed as standard deviation in units of `y`.
        :param thresh_width: The maximum ratio of the fitted to expected
            beamwidth
        :return: The fitted beam parameters (centre, width, height and their
            uncertainties)
        """
        self._interp.fit(x, y, std_y)
        self.centre = self._interp.mean
        self.width = _sigma_to_fwhm(self._interp.std)
        self.height = self._interp.height
        self.std_centre = self._interp.std_mean
        self.std_width = _sigma_to_fwhm(self._interp.std_std)
        self.std_height = self._interp.std_height
        self.is_valid = not any(numpy.isnan(self.centre)) and self.height > 0.0

        # Validation of the fitted beam using SNR and the size of the
        # fitted width compared to the expected. The fitted beam can
        # only be equal to the expected or greater than the expected
        # by less than thresh_width
        fit_snr = self._interp.std / self._interp.std_std
        norm_width = self.width / self.expected_width

        self.is_valid &= (
            all(norm_width > 0.9)
            and all(norm_width < thresh_width)
            and all(fit_snr) > 0.0
        )


class SolveForOffsets:
    """
    Fit the beam pattern to the visibility or gain amplitudes and
    outputs the fitted parameters and their uncertainties.

    :param x_per_scan: Antenna pointings in AzEl coordinates for
        each discrete offset pointing scan with shape [number of
        scans, number of antennas, 2]
    :param y_per_scan: Visibility or gain amplitudes of each antenna
        for each discrete pointing scan with shape [number of antennas,
        number of scans]
    :param freqs: List of frequencies for estimating the expected
        beamwidth
    :param beamwidth_factor: The beamwidth factor for the two orthogonal
        directions. Two values are expected as one value for the horizontal
        direction and the other value for the vertical direction. These
        values often range between 1.03 and 1.22 depending on the illumination
        pattern of the dish
    :param ants: List of katpoint antennas.
    :param thresh_width: The maximum threshold on the allowable fitted
        beamwidth
    """

    def __init__(
        self,
        x_per_scan,
        y_per_scan,
        freqs,
        beamwidth_factor,
        ants,
        thresh_width,
    ):
        self.x_per_scan = x_per_scan
        self.y_per_scan = y_per_scan
        self.freqs = freqs
        self.beamwidth_factor = beamwidth_factor
        self.ants = ants
        self.thresh_width = thresh_width

        # Collect the fitted beams
        self.beams = {}

    def fit_to_visibilities(self):
        """
        Fit the primary beams to the visibility amplitude of each antenna
        and returns the fitted parameters and their uncertainties.

        :return: The fitted beams (parameters and their uncertainties)
        """
        # Calculate the theoretical or expected beamwidth
        # Convert power beamwidth (for single dish) to gain/voltage
        # beamwidth (interferometer)
        log.info("Fitting primary beams to visibility amplitudes...")
        for i, antenna in enumerate(self.ants):
            wavelength = lightspeed / self.freqs
            if not numpy.all(numpy.isfinite(wavelength)):
                raise ValueError(
                    "Wavelength cannot be infinite. Check frequency range!"
                )
            expected_width = numpy.sqrt(2) * numpy.degrees(
                numpy.array(self.beamwidth_factor)
                * wavelength
                / antenna.diameter
            )
            fitted_beam = BeamPatternFit(
                centre=(0.0, 0.0), width=expected_width, height=1.0
            )
            fitted_beam.fit(
                x=self.x_per_scan[:, i].T,
                y=self.y_per_scan[
                    i,
                ],
                std_y=1.0,
                thresh_width=self.thresh_width,
            )

            # Collect the fitted beams
            beams_freq = self.beams.get(antenna.name, [None])
            beams_freq = fitted_beam
            self.beams[antenna.name] = beams_freq

        return self.beams

    def fit_to_gains(self, weights, num_chunks=16):
        """
        Fit the primary beams to the gain amplitudes of each antenna
        and returns the fitted parameters and their uncertainties.

        :param weights: The weights from the gain calibration
        :param num_chunks: Number of chunks used in the gain calibration
        :return: The fitted beams (parameters and their uncertainties)
        """
        # Compute the expected or theoretical beamwidth
        if num_chunks > 1:
            # Exclude the band edges gains, weights, and frequencies
            # solutions by discarding the bottom and top part of the
            # band solutions
            self.y_per_scan = self.y_per_scan[:, 1 : num_chunks - 1]
            weights = weights[:, 1 : num_chunks - 1]
            self.freqs = self.freqs[1 : num_chunks - 1]
        for i, antenna in enumerate(self.ants):
            # Convert power beamwidth (for single dish) to gain/voltage
            # beamwidth (interferometer)
            if num_chunks > 1:
                for chunk in range(num_chunks - 2):
                    wavelength = lightspeed / self.freqs[chunk]
                    if not numpy.all(numpy.isfinite(wavelength)):
                        raise ValueError(
                            "Wavelength cannot be infinite. Check "
                            "frequency range!"
                        )
                    expected_width = numpy.sqrt(2) * numpy.degrees(
                        numpy.array(self.beamwidth_factor)
                        * wavelength
                        / antenna.diameter
                    )
                    log.info(
                        "Fitting primary beams to Band %d gain amplitudes...",
                        chunk + 1,
                    )
                    fitted_beam = BeamPatternFit(
                        centre=(0.0, 0.0), width=expected_width, height=1.0
                    )
                    fitted_beam.fit(
                        x=self.x_per_scan[:, i].T,
                        y=self.y_per_scan[i, chunk],
                        std_y=numpy.sqrt(1.0 / weights[i, chunk]),
                        thresh_width=self.thresh_width,
                    )

                    # Collect the fitted beams
                    beams_freq = self.beams.get(
                        antenna.name, [None] * (num_chunks - 2)
                    )
                    beams_freq[chunk] = fitted_beam
                    self.beams[antenna.name] = beams_freq
            else:
                wavelength = lightspeed / self.freqs
                if not numpy.all(numpy.isfinite(wavelength)):
                    raise ValueError(
                        "Wavelength cannot be infinite. Check frequency range!"
                    )
                expected_width = numpy.sqrt(2) * numpy.degrees(
                    numpy.array(self.beamwidth_factor)
                    * wavelength
                    / antenna.diameter
                )

                log.info("Fitting primary beams to gain amplitudes...")
                fitted_beam = BeamPatternFit(
                    centre=(0.0, 0.0),
                    width=expected_width,
                    height=1.0,
                )

                fitted_beam.fit(
                    x=self.x_per_scan[:, i].T,
                    y=self.y_per_scan[
                        i,
                    ],
                    std_y=numpy.sqrt(
                        1.0
                        / weights[
                            i,
                        ]
                    ),
                    thresh_width=self.thresh_width,
                )

                # Collect the fitted beams
                beams_freq = self.beams.get(antenna.name, [None])
                beams_freq = fitted_beam
                self.beams[antenna.name] = beams_freq

        return self.beams
