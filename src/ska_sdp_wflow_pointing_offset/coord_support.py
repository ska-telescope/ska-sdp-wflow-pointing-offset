# pylint: disable=too-many-arguments, unexpected-keyword-arg
# pylint: disable=no-value-for-parameter
"""
Coordinates support functions
"""

import katpoint
import numpy
import pyuvdata


def construct_antennas(xyz, diameter, station):
    """
    Construct list of katpoint antenna objects
    based on telescope configuration information.

    :param xyz: xyz coordinates of antenna positions in [nants, 3]
    :param diameter: Diameter of dishes in [nants]
    :param station: List of the antenna names [nants]
    :return: a set of katpoint.Antenna objects
    """
    latitude, longitude, altitude = pyuvdata.utils.LatLonAlt_from_XYZ(
        xyz=xyz, frame="ITRS", check_acceptability=True
    )
    ants = []
    for ant_name, diam, lat, long, alt in zip(
        station,
        diameter,
        numpy.squeeze(numpy.radians(latitude)),
        numpy.squeeze(numpy.radians(longitude)),
        numpy.squeeze(altitude),
    ):
        # Antenna information
        # the beam width is HPBW of an antenna: k * lambda/D
        # Currently we use an estimate of 1.22
        ant = katpoint.Antenna(
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
