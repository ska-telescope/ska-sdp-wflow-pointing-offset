"""
Coordinates support functions
"""

import numpy as np
import katpoint


def construct_antennas(xyz, diameter, station):
    """
    Construct list of katpoint antenna objects based on telescope configuration information.
    For MeerKAT, this is not needed, it is only required for SKA-MID.
    The MID configuration file can be found at:
    https://gitlab.com/ska-telescope/sdp/ska-sdp-datamodels.git
    Use:
    x, y, z, diameter, station = np.loadtxt('ska1mid.cfg', dtype=object, unpack=True)
    xyz = np.column_stack((x, y, z))

    :param xyz: xyz coordinates of antenna positions in [nants, 3]
    :param diameter: Diameter of dishes in [nants]
    :param station: List of the antenna names [nants]
    :return: a set of Antenna objects
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


def convert_coordinates(ants, beam_centre, target_coord, timestamps, target_projection):
    """
    Calculate (az, el) given a set of information on beam and target.

    :param ants: Katpoint antenna objects [nants] (from metadata or config file)
    :param beam_centre: Beam centre information (x, y)
    :param target_coord: astropy SkyCoord object that contains RA, Dec information
    :param timestamps: numpy array size [ndumps] (from MS)
    :param target_projection: What coordinate system are we using (str) (from metadata)
    :return: (az, el) coordinates in [nants, 2], radians
    """
    # Target information
    ra = target_coord.ra.rad
    dec = target_coord.dec.rad
    target = katpoint.construct_radec_target(ra, dec)

    az = np.zeros(len(ants))
    el = np.zeros(len(ants))
    for i, antenna in enumerate(ants):

        # Convert from (x,y) to (az, el), output in rad
        # Only doing it for a single timestamp at the moment
        az, el = target.plane_to_sphere(
            x=beam_centre[0],
            y=beam_centre[1],
            timestamp=np.median(timestamps),
            antenna=antenna,
            projection_type=target_projection,
            coord_system="azel",
        )

    return az, el
