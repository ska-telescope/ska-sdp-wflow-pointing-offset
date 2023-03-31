# pylint: disable=too-many-arguments,too-many-locals
# pylint: disable=too-many-instance-attributes,abstract-method
"""
Fits primary beams modelled by a 2D Gaussian to the visibility
amplitudes and computes the azimuth and elevation offsets.
This follows the routines used by the SARAO team for the MeerKAT
array.
"""

import logging

import numpy
from katpoint import lightspeed, wrap_angle
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
    its maximum value.
    """
    # Gaussian function reaches half its peak value at sqrt(2 log 2)*sigma
    return fwhm / 2.0 / numpy.sqrt(2.0 * numpy.log(2.0))


def _sigma_to_fwhm(sigma):
    """
    FWHM beamwidth of Gaussian function with specified standard
    deviation.

    :param sigma: The standard deviation of a Gaussian beam pattern
    with a specified full-width half-maximum (FWHM) beamwidth.
    :return: The full-width half-maximum (FWHM) beamwidth of a Gaussian
    beam pattern with a specified standard deviation. This beamwidth
    is the width between the two points left and right of the peak
    where the Gaussian function attains half its maximum value.
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
        coordinate units.
    :param width: Initial guess of single beam width for both dimensions,
        or 2-element beam width vector, expressed as FWHM in units of
        target coordinates.
    :param height: Initial guess of beam pattern amplitude or height.

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

    def fit(self, x, y, std_y=1.0):
        """
        Fit a beam pattern to data.
        The centre, width and height of the fitted beam pattern
        (and their standard errors) can be obtained from the
        corresponding member variables after this is run.

        :param x: Sequence of (2, N) target coordinates (as column vectors)
        :param y: Sequence of (N, ) corresponding total power values to fit
        :param std_y: Optional measurement error or uncertainty of (N, ) `y`
            values, expressed as standard deviation in units of `y`.
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
        # Set some constraints on the fitted beam width to ensure the width is
        # not larger than some fraction of the expected width
        norm_width = self.width / self.expected_width
        self.is_valid &= all(norm_width > 0.9) and all(norm_width < 1.25)


def fit_primary_beams(
    avg_vis,
    freqs,
    corr_type,
    vis_weights,
    ants,
    source_offsets,
    beam_width_factor,
):
    """
    Fit the beam pattern to the frequency-averaged and optionally
    polarisation-averaged visibilities and outputs the fitted
    parameters and their uncertainties. These visibilities could
    be for each antenna or baseline.

    :param avg_vis: Frequency-averaged visibilities in [ncorr, npol].
    :param freqs: Array of frequencies.
    :param corr_type: The correlation products type of interest.
    :param vis_weights: The weights of the visibilities [ncorr, ] ->
        [timestamps, antennas or baselines]
    :param ants: List of antenna information built in katpoint.
    :param source_offsets: Offsets from the target in Az, El coordinates
        with shape [2, number of timestamps, number of antennas].
    :param beam_width_factor: beamwidth factor between 1.03 and 1.22
        depending on the illumination pattern of the dish.
    :return: The fitted beam centre and uncertainty, fitted beamwidth and
        uncertainty, fitted beam height and uncertainty for each polarisation.
    """
    # Compute the primary beam size for use as initial parameter of the
    # Gaussian. Use higher end of the frequency band with smallest beam
    # for better pointing accuracy
    # Convert power beamwidth to gain / voltage beamwidth
    wavelength = numpy.degrees(lightspeed / freqs[-1])

    # Fit to the visibilities for each polarisation
    log.info("Fitting primary beams to cross-correlation visibilities")
    fitted_centre_pol1 = numpy.zeros((len(ants), 2))
    fitted_centre_std_pol1 = numpy.zeros((len(ants), 2))
    fitted_width_pol1 = numpy.zeros((len(ants), 2))
    fitted_width_std_pol1 = numpy.zeros((len(ants), 2))
    fitted_height_pol1 = numpy.zeros((len(ants), 2))
    fitted_centre_pol2 = numpy.zeros((len(ants), 2))
    fitted_centre_std_pol2 = numpy.zeros((len(ants), 2))
    fitted_width_pol2 = numpy.zeros((len(ants), 2))
    fitted_width_std_pol2 = numpy.zeros((len(ants), 2))
    fitted_height_pol2 = numpy.zeros((len(ants), 2))
    for vis, weight, corr in zip(avg_vis, vis_weights, corr_type):
        log.info("\nFitting of primary beams to %s", corr)
        # Since the x parameter required for the fitting has shape
        # (2, number of timestamps, number of antennas), we need to
        # find a way to reshape the cross-correlation visibilities
        # to include number of antennas instead of baselines.
        # Is this the correct way to do it? To be addressed by
        # ORC-1572 ticket
        vis = vis.reshape(
            source_offsets.shape[1],
            int(vis.shape[0] / source_offsets.shape[1] / len(ants)),
            len(ants),
        )
        weight = weight.reshape(
            source_offsets.shape[1],
            int(weight.shape[0] / source_offsets.shape[1] / len(ants)),
            len(ants),
        )
        vis = numpy.mean(vis, axis=1)
        weight = numpy.mean(weight, axis=1)
        for i, antenna in enumerate(ants):
            # Assume using the default beamwidth factor of 1.22
            expected_width = numpy.sqrt(2.0) * (
                beam_width_factor * wavelength / antenna.diameter
            )
            expected_width = (0.8 * expected_width, 0.9 * expected_width)
            fitted_beam = BeamPatternFit(
                centre=(0.0, 0.0), width=expected_width, height=1.0
            )

            log.info(
                "Fitting primary beam to visibilities of %s", antenna.name
            )
            fitted_beam.fit(
                x=source_offsets[:, :, i],
                y=vis[:, i],
                std_y=numpy.sqrt(1 / weight[:, i]),
            )

            # The fitted beam centre is the AzEl offsets of interest
            # Store the fitted parameters and their uncertainties
            valid_fit = numpy.all(
                numpy.isfinite(
                    numpy.r_[
                        fitted_beam.centre,
                        fitted_beam.std_centre,
                        fitted_beam.width,
                        fitted_beam.std_width,
                        fitted_beam.height,
                        fitted_beam.std_height,
                    ]
                )
            )
            if valid_fit:
                if corr in ("XX", "RR"):
                    fitted_centre_pol1[i] = wrap_angle(fitted_beam.centre)
                    fitted_centre_std_pol1[i] = wrap_angle(
                        fitted_beam.std_centre
                    )
                    fitted_width_pol1[i] = wrap_angle(fitted_beam.width)
                    fitted_width_std_pol1[i] = wrap_angle(
                        fitted_beam.std_width
                    )
                    fitted_height_pol1[i] = (
                        fitted_beam.height,
                        fitted_beam.std_height,
                    )
                elif corr in ("YY", "LL"):
                    fitted_centre_pol2[i] = wrap_angle(fitted_beam.centre)
                    fitted_centre_std_pol2[i] = wrap_angle(
                        fitted_beam.std_centre
                    )
                    fitted_width_pol2[i] = wrap_angle(fitted_beam.width)
                    fitted_width_std_pol2[i] = wrap_angle(
                        fitted_beam.std_width
                    )
                    fitted_height_pol2[i] = (
                        fitted_beam.height,
                        fitted_beam.std_height,
                    )
            else:
                log.warning("No valid primary beam fit for %s", antenna.name)

    # Proposed format for now: Fitted beam centre and uncertainty,
    # fitted beam width and uncertainty, fitted beam height and
    # uncertainty for each polarisation
    return numpy.column_stack(
        (
            fitted_centre_pol1,
            fitted_centre_std_pol1,
            fitted_width_pol1,
            fitted_width_std_pol1,
            fitted_height_pol1,
            fitted_centre_pol2,
            fitted_centre_std_pol2,
            fitted_width_pol2,
            fitted_width_std_pol2,
            fitted_height_pol2,
        )
    )
