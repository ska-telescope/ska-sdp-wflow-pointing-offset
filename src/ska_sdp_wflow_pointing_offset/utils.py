"""
Util functions for constructing katpoint antenna information
"""
from katpoint import Antenna
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
