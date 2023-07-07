"""
Util functions for constructing katpoint antenna information
and solving for antenna gains.
"""
import numpy
from katpoint import Antenna, wrap_angle
from ska_sdp_func_python.calibration import solve_gaintable
from ska_sdp_func_python.util.coordinate_support import ecef_to_lla


def construct_antennas(xyz, diameter, station):
    """
    Construct list of katpoint antenna objects
    based on telescope configuration information.

    :param xyz: xyz coordinates of antenna positions in [nants, 3]
    :param diameter: Diameter of dishes in [nants]
    :param station: List of the antenna names [nants]
    :return: a set of katpoint.Antenna objects
    """
    latitude, longitude, altitude = ecef_to_lla(
        x=xyz[:, 0], y=xyz[:, 1], z=xyz[:, 2]
    )
    ants = []
    for ant_name, diam, lat, long, alt in zip(
        station, diameter, latitude, longitude, altitude
    ):
        # Antenna information
        # The beamwidth is HPBW of an antenna: k * lambda/D
        # We use an estimate of k=1.22 but not used in
        # calculating the beamwidth as k is passed from
        # the command line. The "beamwidth" as used in ant is
        # actually referring to the beamwidth factor, k.
        ant = Antenna(
            name=ant_name,
            latitude=lat,
            longitude=long,
            altitude=alt,
            diameter=diam,
            delay_model=None,
            pointing_model=None,
            beamwidth=1.22,
        )
        ants.append(ant)

    return ants


def compute_gains(vis):
    """
    Solves for the antenna gains for the parallel hands only.

    :param vis: Visibility containing the observed data_models
    :return: GainTable containing solution
    """
    gt_list = solve_gaintable(
        vis=vis,
        modelvis=None,
        gain_table=None,
        phase_only=False,
        niter=200,
        tol=1e-06,
        crosspol=False,
        normalise_gains=None,
        jones_type="G",
        timeslice=None,
    )

    return gt_list


def deproject_from_plane_to_sphere(
    beam_centre_xy, offset_timestamps, ants, target
):
    """
    Convert fitted centre to spherical (az, el) coordinates

    :param beam_centre_xy: The weighted average of the fitted centres
        in ARC xy coordinates in units of radians
    :param offset_timestamps: The antenna pointing timestamps
    :param ants: List of katpoint antennas
    :param target: katpoint target
    :return: Azimuth and elevation offsets in radians
    """
    azel_offset = numpy.full((len(ants), 2), numpy.nan)
    for i, antenna in enumerate(ants):
        beam_centre_azel = target.plane_to_sphere(
            *beam_centre_xy,
            timestamp=numpy.median(offset_timestamps),
            antenna=antenna,
            projection_type="ARC",
            coord_system="azel",
        )
        requested_azel = target.azel(
            timestamp=numpy.median(offset_timestamps), antenna=antenna
        )

        # Calculate the azimuth and elevation offsets
        azel_offset[i] = wrap_angle(
            numpy.array(beam_centre_azel) - numpy.array(requested_azel)
        )

    return azel_offset
