"""
Fits primary beams modelled by a 2D Gaussian to the visibility
amplitudes and computes the true position of the calibrator for
computing the azimuth and elevation offsets. This follows the
routines used by the SARAO team for the MeerKAT array.
"""

import numpy
from katpoint import lightspeed, wrap_angle
from scikits.fitting import GaussianFit, ScatterFit

from src.ska_sdp_wflow_pointing_offset.coord_support import convert_coordinates


def fwhm_to_sigma(fwhm):
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


def sigma_to_fwhm(sigma):
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

    Parameters
    ----------
    :param center: Initial guess of 2-element beam center, in target
    coordinate units
    :param width:Initial guess of single beamwidth for both dimensions,
    or 2-element beamwidth vector, expressed as FWHM in units of target
    coordinates
    :param height: Initial guess of beam pattern amplitude or height

    Attributes
    ----------
    expected_width : real array, shape (2,), or float
        Initial guess of beamwidth, saved as expected width for checks
    is_valid : bool
        True if beam parameters are within reasonable ranges after fit
    std_center : array of float, shape (2,)
        Standard error of beam center, only set after :func:`fit`
    std_width : array of float, shape (2,), or float
        Standard error of beamwidth(s), only set after :func:`fit`
    std_height : float
        Standard error of beam height, only set after :func:`fit`
    """

    def __init__(self, center, width, height):
        ScatterFit.__init__(self)
        if not numpy.isscalar(width):
            width = numpy.atleast_1d(width)
        self._interp = GaussianFit(center, fwhm_to_sigma(width), height)
        self.center = self._interp.mean
        self.width = sigma_to_fwhm(self._interp.std)
        self.height = self._interp.height
        self.expected_width = width
        self.is_valid = False
        self.std_center = self.std_width = self.std_height = None

    def fit(self, x, y, std_y=1.0):
        """
        Fit a beam pattern to data.
        The center, width and height of the fitted beam pattern
        (and their standard errors) can be obtained from the
        corresponding member variables after this is run.

        :param x : Sequence of (2, N) target coordinates (as column vectors)
        :param y : Sequence of (N, ) corresponding total power values to fit
        :param std_y : Optional measurement error or uncertainty of (N, ) `y`
        values, expressed as standard deviation in units of `y`
        :return: The fitted beam parameters (center, width, height and their
        uncertainties)
        """
        self._interp.fit(x, y, std_y)
        self.center = self._interp.mean
        self.width = sigma_to_fwhm(self._interp.std)
        self.height = self._interp.height
        self.std_center = self._interp.std_mean
        self.std_width = sigma_to_fwhm(self._interp.std_std)
        self.std_height = self._interp.std_height
        self.is_valid = not any(numpy.isnan(self.center)) and self.height > 0.0
        # XXX: POTENTIAL TWEAK
        norm_width = self.width / self.expected_width
        self.is_valid &= all(norm_width > 0.9) and all(norm_width < 1.25)

    def __call__(self, x):
        """
        Evaluate fitted beam pattern function on new target coordinates.

        :param x : Sequence of (2, M) target coordinates (as column vectors)
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
    dish_diameter,
    dish_coordinates,
    target,
    target_projection="ARC",
    beamwidth_factor=1.22,
    auto=False,
    split_pol=False,
):
    """
    Fit the beam pattern to the frequency-averaged and optionally polarisation-averaged
    visibilities and outputs the fitted parameters and their uncertainties. These visibilities
    could be for each antenna or baseline.

    :param avg_vis: Frequency-averaged visibilities.
    :param freqs: Array of frequencies.
    :param timestamps: Array of observation timestamps.
    :param corr_type: The correlation products type of interest.
    :param vis_weight: The weights of the visibilities [ncorr, ] -> [timestamps, antennas or baselines]
    :param ants: Lst of antenna information built in katpoint.
    :param dish_diameter: Diameter of the dish in the array. Expected to be the same. Different
    dish diameters is not currently supported.
    :param dish_coordinates: Projections of the spherical coordinates of the dish pointing
    direction to a plane with the target position at the origin. Shape is [2, number of timestamps,
    number of antennas].
    :param target: katpoint pointing calibrator information (optionally source name, RA, DEC)
    :param target_projection: The projection used in the observation.
    :param beamwidth_factor: Beamwidth factor (often between 1.03 and 1.22).
    :param auto: Use auto-correlation visibilities?
    :param split_pol: Fit primary beam to the visibilities of the parallel hand polarisations?
    :return: Fitted beam parameters and their uncertainties.
    """
    # Compute the primary beam size for use as initial parameter of the Gaussian
    # Use higher end of the frequency band with smallest beam for better pointing accuracy
    # Convert power beamwidth to gain / voltage beamwidth
    wavelength = numpy.degrees(lightspeed / freqs[-1])
    expected_width = numpy.sqrt(2.0) * (
        beamwidth_factor * wavelength / dish_diameter
    )

    # XXX This assumes we are still using default beamwidth factor of 1.22
    # and also handles larger effective dish diameter in H direction. Note that the comment
    # applies to the MeerKAT but would that apply to the SKA ?
    expected_width = (0.8 * expected_width, 0.9 * expected_width)
    fitted_beam = BeamPatternFit(
        center=(0.0, 0.0), width=expected_width, height=1.0
    )

    # TO Do: Test primary beam fitting to the cross-correlation visibilities
    if auto:
        # Split number of correlations -> (timestamps, antennas) for per antenna fitting
        print("Fitting primary beams to auto-correlation visibilities")
    else:
        # Split number of correlations -> (timestamps, baseline) for per baseline fitting
        print("Fitting primary beams to cross-correlation visibilities")

    # Begin fitting the primary beam to the visibilities
    if split_pol:
        # Fit to the visibilities of each polarisation
        for vis, weight, corr in zip(avg_vis, vis_weight, corr_type):
            print(f"\nFitting of primary beams to {corr}")
            if auto:
                vis = vis.reshape(
                    len(timestamps), int(vis.shape[0] / len(timestamps))
                )
                weight = weight.reshape(
                    len(timestamps), int(weight.shape[0] / len(timestamps))
                )
            else:
                # Since the x parameter required for the fitting has shape (2, number of timestamps, number of antennas),
                # we need to find a way to reshape the cross-correlation visibilities to include number of antennas instead of baselines.
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
            for i in range(vis.shape[1]):
                print(
                    f"Fitting primary beam to visibilities of Antenna {ants[i].name}"
                )
                fitted_beam.fit(
                    x=dish_coordinates[:, :, i],
                    y=vis[:, i],
                    std_y=numpy.sqrt(1 / weight)[:, i],
                )
                center_norm = numpy.radians(
                    fitted_beam.center / fitted_beam.std_center
                )
                width_norm = numpy.radians(fitted_beam.center / expected_width)

                # Convert the fitted beam centre from (x,y) to (az,el)
                try:
                    fitted_az, fitted_el = convert_coordinates(
                        ant=ants[i],
                        beam_center=center_norm,
                        timestamps=timestamps,
                        target_projection=target_projection,
                        target_object=target,
                    )
                    requested_az, requested_el = target.azel(
                        timestamp=numpy.median(timestamps), antenna=ants[i]
                    )
                    fitted_az, fitted_el = numpy.degrees(
                        fitted_az
                    ), numpy.degrees(fitted_el)
                    requested_az, requested_el = numpy.degrees(
                        requested_az
                    ), numpy.degrees(requested_el)
                    offset_az, offset_el = wrap_angle(
                        fitted_az - requested_az, 360.0
                    ), wrap_angle(fitted_el - requested_el, 360.0)
                    # print(
                    #    f"Centre=({center_norm[0]:.8f},{center_norm[1]:.8f}), Width=({width_norm[0]:.8f},{width_norm[1]:.8f})"
                    # )
                    print(offset_az, offset_el)
                except:
                    print(f"No valid primary beam fit for {ants[i].name}")
    else:
        # Fit to the frequency-polarisation-averaged visibilities
        if auto:
            avg_vis = avg_vis.reshape(
                len(timestamps), int(avg_vis.shape[0] / len(timestamps))
            )
            vis_weight = vis_weight.reshape(
                len(timestamps), int(vis_weight.shape[0] / len(timestamps))
            )
        else:
            # Since the x parameter required for the fitting has shape (2, number of timestamps, number of antennas),
            # we need to find a way to reshape the cross-correlation visibilities to include number of antennas instead of baselines.
            # Is this the correct way to do it?
            avg_vis = avg_vis.reshape(
                len(timestamps),
                int(avg_vis.shape[0] / len(timestamps) / len(ants)),
                len(ants),
            )
            vis_weight = vis_weight.reshape(
                len(timestamps),
                int(vis_weight.shape[0] / len(timestamps) / len(ants)),
                len(ants),
            )
            avg_vis = numpy.mean(avg_vis, axis=1)
            vis_weight = numpy.mean(vis_weight, axis=1)

        for i in range(avg_vis.shape[1]):
            # print(
            #    f"\nFitting primary beam to visibilities of Antenna {ants[i].name}"
            # )
            fitted_beam.fit(
                x=dish_coordinates[:, :, i],
                y=avg_vis[:, i],
                std_y=numpy.sqrt(1 / vis_weight)[:, i],
            )
            center_norm = numpy.radians(
                fitted_beam.center / fitted_beam.std_center
            )
            width_norm = numpy.radians(fitted_beam.center / expected_width)

            # Convert the fitted beam centre from (x,y) to (az,el)
            try:
                fitted_az, fitted_el = convert_coordinates(
                    ant=ants[i],
                    beam_center=center_norm,
                    timestamps=timestamps,
                    target_projection=target_projection,
                    target_object=target,
                )
                requested_az, requested_el = target.azel(
                    timestamp=numpy.median(timestamps), antenna=ants[i]
                )

                fitted_az, fitted_el = numpy.degrees(fitted_az), numpy.degrees(
                    fitted_el
                )
                requested_az, requested_el = numpy.degrees(
                    requested_az
                ), numpy.degrees(requested_el)
                offset_az, offset_el = wrap_angle(
                    fitted_az - requested_az, 360.0
                ), wrap_angle(fitted_el - requested_el, 360.0)
                # print(
                #    f"Centre=({center_norm[0]:.8f},{center_norm[1]:.8f}), Width=({width_norm[0]:.8f},{width_norm[1]:.8f})"
                # )
                print(offset_az, offset_el)
            except:
                print(f"\nNo valid primary beam fit for {ants[i].name}")
