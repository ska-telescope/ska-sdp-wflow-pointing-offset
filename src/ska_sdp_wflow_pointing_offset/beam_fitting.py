# pylint: disable=too-many-instance-attributes,abstract-method
# pylint: disable=too-many-locals,too-many-arguments
# pylint: disable=too-many-statements,too-many-branches
"""
Fits primary beams modelled by a 2D Gaussian to the visibility
or gain amplitudes and computes the elevation and cross-elevation
offsets. This follows the routines used by the SARAO team for the
MeerKAT array.
"""

import logging

import numpy
from katpoint import lightspeed, wrap_angle
from scikits.fitting import GaussianFit, ScatterFit
from uncertainties import unumpy

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

    def fit(self, x, y, std_y=1.0, thresh_width=1.5):
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

        self.is_valid &= (0.9 < norm_width < thresh_width) and fit_snr > 0.0


class SolveForOffsets:
    """
    Fit the beam pattern to the frequency-averaged visibility amplitudes
    or gain amplitudes and outputs the fitted parameters and their
    uncertainties.

    :param source_offset: Offsets from the target in Az, El coordinates
        with shape [2, number of timestamps, number of antennas]
    :param actual_pointing_el: The interpolated actual pointing
        elevation with shape [ntimes, number of antennas] to be used
        in calculating the cross-elevation offsets. The cross-elevation
        offset is the product of the azimuth-offset and cosine of the
        median actual pointing elevation.
    :param y_param: Visibility containing the observed data or
        amplitude gains of each antenna
    :param beamwidth_factor: The beamwidth factor for the two orthogonal
        directions. Two values are expected as one value for the horizontal
        direction and the other value for the vertical direction. These
        values often range between 1.03 and 1.22 depending on the illumination
        pattern of the dish
    :param ants: List of antenna information built in katpoint.
    """

    def __init__(
        self,
        source_offset,
        actual_pointing_el,
        y_param,
        beamwidth_factor,
        ants,
        thresh_width,
    ):
        self.source_offset = source_offset
        self.actual_pointing_el = actual_pointing_el
        self.y_param = y_param
        self.beamwidth_factor = beamwidth_factor
        self.ants = ants
        self.thresh_width = thresh_width
        self.wavelength = lightspeed / self.y_param.frequency.data
        if not numpy.all(numpy.isfinite(self.wavelength)):
            raise ValueError(
                "Wavelength cannot be infinite. Check frequency range!"
            )

        # Compute the expected width here
        self.expected_width = []
        for antenna in self.ants:
            # Convert power beamwidth (for single dish) to gain/voltage
            # beamwidth (interferometer)
            expected_width_h = numpy.sqrt(2) * numpy.degrees(
                self.beamwidth_factor[0] * self.wavelength / antenna.diameter
            )
            expected_width_v = numpy.sqrt(2) * numpy.degrees(
                self.beamwidth_factor[1] * self.wavelength / antenna.diameter
            )
            self.expected_width.append([expected_width_h, expected_width_v])

        # Fitted parameters of interest for each pol per antenna to be
        # saved to file
        self.azel_offset_pol1 = numpy.zeros((len(self.ants), 2))
        self.azel_offset_std_pol1 = numpy.zeros((len(self.ants), 2))
        self.cross_el_pol1 = numpy.zeros((len(self.ants), 2))
        self.fitted_width_pol1 = numpy.zeros((len(self.ants), 2))
        self.fitted_width_std_pol1 = numpy.zeros((len(self.ants), 2))
        self.fitted_height_pol1 = numpy.zeros((len(self.ants), 2))

        self.azel_offset_pol2 = numpy.zeros((len(self.ants), 2))
        self.azel_offset_std_pol2 = numpy.zeros((len(self.ants), 2))
        self.cross_el_pol2 = numpy.zeros((len(self.ants), 2))
        self.fitted_width_pol2 = numpy.zeros((len(self.ants), 2))
        self.fitted_width_std_pol2 = numpy.zeros((len(self.ants), 2))
        self.fitted_height_pol2 = numpy.zeros((len(self.ants), 2))

    def fit_to_visibilities(self):
        """
        Fit primary beams to the visibility amplitude of each antenna. The
        baseline-based visibilities are converted to antenna-based visibilities
        before the fitting is performed. Since the x-parameter required for
        the fitting has shape (ntimes, number of antennas, 2), we need to
        find a way to translate baseline-based to antenna-based visibilities.
        Is this a robust/correct way to do it - to be investigated with
        ORC-1572 ticket.

        :return: The fitted beam centre and uncertainty, fitted beamwidth and
        uncertainty, fitted beam height and uncertainty for each polarisation
        """
        # Average the parallel hand visibilities in frequency but ignoring
        # the visibility weights for now. The MS reader used in this
        # pipeline reads the data in the "WEIGHT" column but the different
        # weights should be used when averaging the raw or corrected data.
        # Details are in the CASA doc on
        # https://casa.nrao.edu/casadocs/casa-6.1.0/global-task-list/task_plotms/about
        corr_type = self.y_param.polarisation.data
        try:
            avg_vis = numpy.mean(self.y_param.vis.data, axis=2)
            if len(corr_type) == 2:
                # (XX,YY) or (RR, LL)
                corr_type = numpy.array(
                    [corr_type[0], corr_type[1]], dtype=object
                )
                avg_vis = numpy.array(
                    [avg_vis[:, :, 0], avg_vis[:, :, 1]],
                    dtype=object,
                )
            elif len(corr_type) == 4:
                # (XX,XY,YX,YY) or (RR,RL,LR,LL)
                corr_type = numpy.array(
                    [corr_type[0], corr_type[3]], dtype=object
                )
                avg_vis = numpy.array(
                    [avg_vis[:, :, 0], avg_vis[:, :, 3]],
                    dtype=object,
                )
            else:
                raise ValueError("Polarisation type not supported")

            _, ntimes, ncorr = avg_vis.shape
            for i, (vis, corr) in enumerate(zip(avg_vis, corr_type)):
                # Reshape and keep only ntimes and ants axes
                log.info("\nFitting primary beams to %s", corr)
                vis = vis.reshape(
                    ntimes, int(ncorr / len(self.ants)), len(self.ants)
                )
                vis = numpy.mean(vis, axis=1)
                for j, antenna in enumerate(self.ants):
                    # Use the higher end of the frequency band to compute
                    # beam size for better pointing accuracy
                    fitted_beam = BeamPatternFit(
                        centre=(0.0, 0.0),
                        width=self.expected_width[j][i][-1],
                        height=1.0,
                    )
                    log.info(
                        "Fitting primary beam to visibilities of %s",
                        antenna.name,
                    )
                    fitted_beam.fit(
                        x=numpy.moveaxis(self.source_offset, 2, 0)[:, :, i],
                        y=numpy.abs(vis).astype(float)[:, j],
                        std_y=1.0,
                        thresh_width=self.thresh_width,
                    )

                    # The fitted beam centre is the AzEl offset
                    # Store the fitted parameters and their uncertainties
                    if fitted_beam.is_valid:
                        # Cross-el offset = azimuth offset*cos(el)
                        elev = numpy.radians(
                            numpy.median(self.actual_pointing_el[:, j])
                        )
                        azel_offset = unumpy.uarray(
                            wrap_angle(numpy.radians(fitted_beam.centre)),
                            numpy.abs(
                                wrap_angle(
                                    numpy.radians(fitted_beam.std_centre)
                                )
                            ),
                        )
                        cross_el_offset = azel_offset[0] * numpy.cos(elev)
                        fitted_width = wrap_angle(
                            numpy.radians(fitted_beam.width)
                        )
                        fitted_width_std = wrap_angle(
                            numpy.radians(fitted_beam.std_width)
                        )
                        fitted_height = (
                            fitted_beam.height,
                            fitted_beam.std_height,
                        )
                        if corr in ("XX", "RR"):
                            self.azel_offset_pol1[j] = unumpy.nominal_values(
                                azel_offset
                            )
                            self.azel_offset_std_pol1[j] = unumpy.std_devs(
                                azel_offset
                            )
                            self.cross_el_pol1[j] = unumpy.nominal_values(
                                cross_el_offset
                            ), unumpy.std_devs(cross_el_offset)
                            self.fitted_width_pol1[j] = fitted_width
                            self.fitted_width_std_pol1[j] = fitted_width_std
                            self.fitted_height_pol1[j] = fitted_height
                        elif corr in ("YY", "LL"):
                            self.azel_offset_pol2[j] = unumpy.nominal_values(
                                azel_offset
                            )
                            self.azel_offset_std_pol2[j] = unumpy.std_devs(
                                azel_offset
                            )
                            self.cross_el_pol2[j] = unumpy.nominal_values(
                                cross_el_offset
                            ), unumpy.std_devs(cross_el_offset)
                            self.fitted_width_pol2[j] = fitted_width
                            self.fitted_width_std_pol2[j] = fitted_width_std
                            self.fitted_height_pol2[j] = fitted_height
                    else:
                        log.warning(
                            "No valid primary beam fit for %s", antenna.name
                        )
        except ValueError:
            # Problems with reshaping baseline-based visibilities to
            # antenna-based
            vis_per_antenna = []
            avg_vis = numpy.mean(self.y_param.vis.data, axis=2)
            for i in range(len(self.ants)):
                # Get the visibilities for each antenna per polarisation
                mask = (self.y_param.antenna1.data == i) ^ (
                    self.y_param.antenna2.data == i
                )
                avg = numpy.mean(avg_vis[:, mask, :], axis=1)
                if len(corr_type) == 2:
                    # (XX,YY) or (RR, LL)
                    corr_type = numpy.array(
                        [corr_type[0], corr_type[1]], dtype=object
                    )
                    vis_per_antenna.append(
                        numpy.array([avg[:, 0], avg[:, 1]], dtype=object)
                    )
                elif len(corr_type) == 4:
                    # (XX,XY,YX,YY) or (RR,RL,LR,LL)
                    corr_type = numpy.array(
                        [corr_type[0], corr_type[3]], dtype=object
                    )
                    vis_per_antenna.append(
                        numpy.array([avg[:, 0], avg[:, 3]], dtype=object)
                    )

            vis_per_antenna = numpy.moveaxis(
                numpy.array(vis_per_antenna), 0, 1
            )
            for j, (vis, corr) in enumerate(zip(vis_per_antenna, corr_type)):
                log.info("\nFitting primary beams to %s", corr)
                for k, antenna in enumerate(self.ants):
                    # Use the higher end of the frequency band to compute
                    # beam size for better pointing accuracy
                    fitted_beam = BeamPatternFit(
                        centre=(0.0, 0.0),
                        width=self.expected_width[k][j][-1],
                        height=1.0,
                    )
                    log.info(
                        "Fitting primary beam to visibilities of %s",
                        antenna.name,
                    )
                    fitted_beam.fit(
                        x=numpy.moveaxis(self.source_offset, 2, 0)[:, :, k],
                        y=numpy.abs(vis).astype(float)[k, :],
                        std_y=1.0,
                        thresh_width=self.thresh_width,
                    )

                    # The fitted beam centre is the AzEl offset
                    # Store the fitted parameters and their uncertainties
                    if fitted_beam.is_valid:
                        # Cross-el offset = azimuth offset*cos(el)
                        elev = numpy.radians(
                            numpy.median(self.actual_pointing_el[:, k])
                        )
                        azel_offset = unumpy.uarray(
                            wrap_angle(numpy.radians(fitted_beam.centre)),
                            numpy.abs(
                                wrap_angle(
                                    numpy.radians(fitted_beam.std_centre)
                                )
                            ),
                        )
                        cross_el_offset = azel_offset[0] * numpy.cos(elev)
                        fitted_width = wrap_angle(
                            numpy.radians(fitted_beam.width)
                        )
                        fitted_width_std = wrap_angle(
                            numpy.radians(fitted_beam.std_width)
                        )
                        fitted_height = (
                            fitted_beam.height,
                            fitted_beam.std_height,
                        )
                        if corr in ("XX", "RR"):
                            self.azel_offset_pol1[k] = unumpy.nominal_values(
                                azel_offset
                            )
                            self.azel_offset_std_pol1[k] = unumpy.std_devs(
                                azel_offset
                            )
                            self.cross_el_pol1[k] = unumpy.nominal_values(
                                cross_el_offset
                            ), unumpy.std_devs(cross_el_offset)
                            self.fitted_width_pol1[k] = fitted_width
                            self.fitted_width_std_pol1[k] = fitted_width_std
                            self.fitted_height_pol1[k] = fitted_height
                        elif corr in ("YY", "LL"):
                            self.azel_offset_pol2[k] = unumpy.nominal_values(
                                azel_offset
                            )
                            self.azel_offset_std_pol2[k] = unumpy.std_devs(
                                azel_offset
                            )
                            self.cross_el_pol2[k] = unumpy.nominal_values(
                                cross_el_offset
                            ), unumpy.std_devs(cross_el_offset)
                            self.fitted_width_pol2[k] = fitted_width
                            self.fitted_width_std_pol2[k] = fitted_width_std
                            self.fitted_height_pol2[k] = fitted_height
                    else:
                        log.warning(
                            "No valid primary beam fit for %s", antenna.name
                        )
        return numpy.column_stack(
            (
                self.azel_offset_pol1,
                self.azel_offset_std_pol1,
                self.cross_el_pol1,
                self.fitted_width_pol1,
                self.fitted_width_std_pol1,
                self.fitted_height_pol1,
                self.azel_offset_pol2,
                self.azel_offset_std_pol2,
                self.cross_el_pol2,
                self.fitted_width_pol2,
                self.fitted_width_std_pol2,
                self.fitted_height_pol2,
            )
        )

    def fit_to_gains(self):
        """
        Fit the primary beams to the amplitude gains of each antenna
        and returns the fitted parameters and their uncertainties.

        :return: The fitted beam centre and uncertainty, cross-elevation
        offset and uncertainty, fitted beamwidth and uncertainty, fitted
        beam height and uncertainty for each polarisation
        """
        # The shape of the gain is ntimes, baselines, 1 (averaged-frequency),
        # receptor1, receptor2
        log.info("\nFitting primary beams to gain amplitudes...")
        gain = numpy.abs(numpy.squeeze(self.y_param.gain.data))
        gain_weight = numpy.squeeze(self.y_param.weight.data)
        receptor1 = self.y_param.receptor1.data
        receptor2 = self.y_param.receptor2.data
        corr = (receptor1[0] + receptor2[0], receptor1[1] + receptor2[1])
        for i, corr in enumerate(corr):
            log.info("\nFitting primary beams to %s", corr)
            for j, antenna in enumerate(self.ants):
                fitted_beam = BeamPatternFit(
                    centre=(0.0, 0.0),
                    width=self.expected_width[j][i],
                    height=1.0,
                )

                log.info(
                    "Fitting primary beam to gain amplitudes of %s",
                    antenna.name,
                )
                fitted_beam.fit(
                    x=numpy.moveaxis(self.source_offset, 2, 0)[:, :, j],
                    y=gain[:, j, i, i],
                    std_y=numpy.sqrt(1 / gain_weight[:, j, i, i]),
                    thresh_width=self.thresh_width,
                )

                # The fitted beam centre is the AzEl offset
                # Store the fitted parameters and their uncertainties
                if fitted_beam.is_valid:
                    # Cross-el offset = azimuth offset*cos(el)
                    elev = numpy.radians(
                        numpy.median(self.actual_pointing_el[:, i])
                    )
                    azel_offset = unumpy.uarray(
                        wrap_angle(numpy.radians(fitted_beam.centre)),
                        numpy.abs(
                            wrap_angle(numpy.radians(fitted_beam.std_centre))
                        ),
                    )
                    cross_el_offset = azel_offset[0] * numpy.cos(elev)
                    fitted_width = wrap_angle(numpy.radians(fitted_beam.width))
                    fitted_width_std = wrap_angle(
                        numpy.radians(fitted_beam.std_width)
                    )
                    fitted_height = fitted_beam.height, fitted_beam.std_height
                    if corr in ("XX", "RR"):
                        self.azel_offset_pol1[i] = unumpy.nominal_values(
                            azel_offset
                        )
                        self.azel_offset_std_pol1[i] = unumpy.std_devs(
                            azel_offset
                        )
                        self.cross_el_pol1[i] = unumpy.nominal_values(
                            cross_el_offset
                        ), unumpy.std_devs(cross_el_offset)
                        self.fitted_width_pol1[i] = fitted_width
                        self.fitted_width_std_pol1[i] = fitted_width_std
                        self.fitted_height_pol1[i] = fitted_height
                    elif corr in ("YY", "LL"):
                        self.azel_offset_pol2[i] = unumpy.nominal_values(
                            azel_offset
                        )
                        self.azel_offset_std_pol2[i] = unumpy.std_devs(
                            azel_offset
                        )
                        self.cross_el_pol2[i] = unumpy.nominal_values(
                            cross_el_offset
                        ), unumpy.std_devs(cross_el_offset)
                        self.fitted_width_pol2[i] = fitted_width
                        self.fitted_width_std_pol2[i] = fitted_width_std
                        self.fitted_height_pol2[i] = fitted_height
                else:
                    log.warning(
                        "No valid primary beam fit for %s", antenna.name
                    )

        # Proposed format for now: AzEl offsets and their uncertainties,
        # Cross-elevation offset and its uncertainty, fitted beam width
        # and its uncertainty, fitted beam height and its uncertainty
        # for each polarisation
        return numpy.column_stack(
            (
                self.azel_offset_pol1,
                self.azel_offset_std_pol1,
                self.cross_el_pol1,
                self.fitted_width_pol1,
                self.fitted_width_std_pol1,
                self.fitted_height_pol1,
                self.azel_offset_pol2,
                self.azel_offset_std_pol2,
                self.cross_el_pol2,
                self.fitted_width_pol2,
                self.fitted_width_std_pol2,
                self.fitted_height_pol2,
            )
        )
