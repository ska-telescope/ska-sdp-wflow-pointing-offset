# pylint: disable=too-many-arguments
"""
Coordinates support functions
"""

import katpoint
import numpy as np


def construct_antennas(xyz, diameter, station):
    """
    Construct list of katpoint antenna objects
    based on telescope configuration information.
    For MeerKAT, this is not needed, it is only required for SKA-MID.
    The MID configuration file can be found at:
    https://gitlab.com/ska-telescope/sdp/ska-sdp-datamodels.git
    Use:
    x, y, z, diameter, station =
    np.loadtxt('ska1mid.cfg', dtype=object, unpack=True)
    xyz = np.column_stack((x, y, z))

    :param xyz: xyz coordinates of antenna positions in [nants, 3]
    :param diameter: Diameter of dishes in [nants]
    :param station: List of the antenna names [nants]
    :return: a set of katpoint.Antenna objects
    """
    import pyuvdata  # pylint: disable=import-error,import-outside-toplevel

    latitude, longitude, altitude = pyuvdata.utils.LatLonAlt_from_XYZ(
        xyz=xyz, frame="ITRS", check_acceptability=True
    )
    ants = []
    for ant_name, diam, lat, long, alt in zip(
        station,
        diameter,
        np.squeeze(np.radians(latitude)),
        np.squeeze(np.radians(longitude)),
        np.squeeze(altitude),
    ):
        # Antenna information
        ant = katpoint.Antenna(
            name=ant_name,  # "SKA1-MID",
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


def convert_coordinates(
    ants,
    beam_centre,
    timestamps,
    target_projection,
    target_object=None,
    target_coord=None,
):
    """
    Calculate (az, el) given a set of information on beam and target.

    :param ants: List of katpoint antenna objects [nants]
                 Either from metadata file,
                 Or from config file and created via
                 constructed_antennas
    :param beam_centre: Beam centre information (x, y)
    :param timestamps: numpy array size [ndumps] (from metadata)
    :param target_projection: Name of coordinate system  (from metadata)
    :param target_object: Katpoint target object (from metadata)
    :param target_coord: SkyCoord object that contains RA, Dec information
                         Only used when katpoint target is not provided
    :return: (az, el) coordinates in [nants, 2], radians
    """

    # Construct target if Katpoint target object is not provided
    if target_object is None:
        target_ra = target_coord.ra.rad
        target_dec = target_coord.dec.rad
        target_object = katpoint.construct_radec_target(target_ra, target_dec)

    az_arr = np.zeros(len(ants))
    el_arr = np.zeros(len(ants))
    for i, antenna in enumerate(ants):

        # Convert from (x,y) to (az, el), output in rad
        # Only doing it for a single timestamp at the moment
        az_arr[i], el_arr[i] = target_object.plane_to_sphere(
            x=beam_centre[0],
            y=beam_centre[1],
            timestamp=np.median(timestamps),
            antenna=antenna,
            projection_type=target_projection,
            coord_system="azel",
        )

    return az_arr, el_arr
