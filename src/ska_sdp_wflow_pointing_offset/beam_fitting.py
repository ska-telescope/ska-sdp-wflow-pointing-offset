# pylint: disable=too-many-arguments,too-many-locals
# pylint: disable=too-many-statements,too-many-instance-attributes
"""
Fits primary beams modelled by a 2D Gaussian to the visibility
amplitudes and computes the true position of the calibrator for
computing the azimuth and elevation offsets. This follows the
routines used by the SARAO team for the MeerKAT array.
"""

import logging

import numpy
from katpoint import lightspeed, wrap_angle
from katpoint.projection import OutOfRangeError
from scikits.fitting import GaussianFit, ScatterFit

from ska_sdp_wflow_pointing_offset.coord_support import convert_coordinates

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
        coordinate units
    :param width: Initial guess of single beamwidth for both dimensions,
        or 2-element beamwidth vector, expressed as FWHM in units of
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
        # We do not know why the fitted width is normalised by the
        # expected width for the MeerKAT array. A request to understand
        # its purpose has been sent to the SARAO team. Note that this may
        # not necessarily apply to the SKA
        norm_width = self.width / self.expected_width
        self.is_valid &= all(norm_width > 0.9) and all(norm_width < 1.25)

    def __call__(self, x):
        """
        Evaluate fitted beam pattern function on new target coordinates.

        :param x: Sequence of (2, M) target coordinates (as column vectors)
        :return: Sequence of total power values (M, ) representing fitted beam
        """
        return self._interp(x)


def fit_primary_beams(
    avg_vis,
    freqs,
    timestamps,
    corr_type,
    vis_weight,
    ants,
    dish_coordinates,
    target,
    target_projection="ARC",
    beamwidth_factor=1.22,
    auto=False,
):
    """
    Fit the beam pattern to the frequency-averaged and optionally
    polarisation-averaged visibilities and outputs the fitted
    parameters and their uncertainties. These visibilities could
    be for each antenna or baseline.

    :param avg_vis: Frequency-averaged visibilities.
    :param freqs: Array of frequencies.
    :param timestamps: Array of observation timestamps.
    :param corr_type: The correlation products type of interest.
    :param vis_weight: The weights of the visibilities [ncorr, ] ->
        [timestamps, antennas or baselines]
    :param ants: List of antenna information built in katpoint. Different
        dish diameters is not currently supported.
    :param dish_coordinates: Projections of the spherical coordinates
        of the dish pointing direction to a plane with the target position
        at the origin. Shape is [2, number of timestamps, number of antennas].
    :param target: katpoint pointing calibrator information (optionally
        source name, RA, DEC)
    :param target_projection: The projection used in the observation.
    :param beamwidth_factor: Beamwidth factor (often between 1.03 and 1.22).
    :param auto: Use auto-correlation visibilities?
    :return: Fitted beam parameters with their uncertainties, and the
        computed pointing offsets.
    """
    # Compute the primary beam size for use as initial parameter of the
    # Gaussian. Use higher end of the frequency band with smallest beam
    # for better pointing accuracy
    # Convert power beamwidth to gain / voltage beamwidth
    wavelength = numpy.degrees(lightspeed / freqs[-1])
    expected_width = numpy.sqrt(2.0) * (
        beamwidth_factor * wavelength / ants[0].diameter
    )

    # Assume using the default beamwidth factor of 1.22
    # for the MeerKAT array, which should handle the
    # larger effective dish diameter in the H direction.
    # Same may not apply for the SKA
    expected_width = (0.8 * expected_width, 0.9 * expected_width)
    fitted_beam = BeamPatternFit(
        centre=(0.0, 0.0), width=expected_width, height=1.0
    )

    # Fit to the visibilities of each polarisation
    if auto:
        log.info("Fitting primary beams to auto-correlation visibilities")
    else:
        log.info("Fitting primary beams to cross-correlation visibilities")
    fitted_centre = numpy.zeros((len(ants), 2))
    fitted_width = numpy.zeros((len(ants), 2))
    fitted_height = numpy.zeros((len(ants), 2))
    fitted_centre_std = numpy.zeros((len(ants), 2))
    fitted_width_std = numpy.zeros((len(ants), 2))
    fitted_height_std = numpy.zeros((len(ants), 2))
    true_azel = numpy.zeros((len(ants), 2))
    commanded_azel = numpy.zeros((len(ants), 2))
    offset_azel = numpy.zeros((len(ants), 2))
    for vis, weight, corr in zip(avg_vis, vis_weight, corr_type):
        log.info("Fitting of primary beams to %s", corr)
        if auto:
            vis = vis.reshape(
                len(timestamps), int(vis.shape[0] / len(timestamps))
            )
            weight = weight.reshape(
                len(timestamps), int(weight.shape[0] / len(timestamps))
            )
        else:
            # Since the x parameter required for the fitting has shape
            # (2, number of timestamps, number of antennas), we need to
            # find a way to reshape the cross-correlation visibilities
            # to include number of antennas instead of baselines.
            # Is this the correct way to do it?
            vis = vis.reshape(
                len(timestamps),
                int(vis.shape[0] / len(timestamps) / len(ants)),
                len(ants),
            )
            weight = weight.reshape(
                len(timestamps),
                int(weight.shape[0] / len(timestamps) / len(ants)),
                len(ants),
            )
            vis = numpy.mean(vis, axis=1)
            weight = numpy.mean(weight, axis=1)
        for i, antenna in enumerate(ants):
            log.info(
                "Fitting primary beam to visibilities of %s", antenna.name
            )
            fitted_beam.fit(
                x=dish_coordinates[:, :, i],
                y=vis[:, i],
                std_y=numpy.sqrt(1 / weight[:, i]),
            )

            # Get the requested AzEl
            requested_az, requested_el = target.azel(
                timestamp=numpy.median(timestamps), antenna=antenna
            )
            requested_az, requested_el = numpy.degrees(
                requested_az
            ), numpy.degrees(requested_el)
            commanded_azel[i] = numpy.column_stack(
                (requested_az, requested_el)
            )

            # Convert the fitted beam centre from (x,y) to (az,el)
            fitted_centre[i] = fitted_beam.centre
            fitted_width[i] = fitted_beam.width
            fitted_height[i] = fitted_beam.height
            fitted_centre_std[i] = fitted_beam.std_centre
            fitted_width_std[i] = fitted_beam.std_width
            fitted_height_std[i] = fitted_beam.std_height
            fitted_beam.centre = numpy.radians(fitted_beam.centre)
            fitted_beam.width = numpy.radians(fitted_beam.width)
            try:
                fitted_az, fitted_el = convert_coordinates(
                    ant=antenna,
                    beam_centre=fitted_beam.centre,
                    timestamps=timestamps,
                    target_projection=target_projection,
                    target_object=target,
                )
                fitted_az, fitted_el = numpy.degrees(fitted_az), numpy.degrees(
                    fitted_el
                )
                offset_az, offset_el = wrap_angle(
                    fitted_az - requested_az, 360.0
                ), wrap_angle(fitted_el - requested_el, 360.0)
                true_azel[i] = numpy.column_stack((fitted_az, fitted_el))
                offset_azel[i] = numpy.column_stack((offset_az, offset_el))
            except OutOfRangeError:
                # This is an out of range error as the fitted (x,y) < np.pi
                true_azel[i] = numpy.column_stack((0.0, 0.0))
                offset_azel[i] = numpy.column_stack((0.0, 0.0))
                log.warning("No valid primary beam fit for %s", antenna.name)

    # Proposed format for now: Antenna Name, Fitting flag, fitted beam centre
    # and uncertainty, fitted beamwidth and uncertainty, fitted beam height and
    # uncertainty, fitted beam centre (in azel), commanded (azel), delta Az,
    # delta El
    return numpy.column_stack(
        (
            fitted_centre,
            fitted_centre_std,
            fitted_width,
            fitted_width_std,
            fitted_height,
            fitted_height_std,
            true_azel,
            commanded_azel,
            offset_azel,
        )
    )
