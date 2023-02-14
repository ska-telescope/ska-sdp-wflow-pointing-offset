# pylint: disable=too-many-arguments, unexpected-keyword-arg
# pylint: disable=no-value-for-parameter
"""
Coordinates support functions
"""

import katpoint
import numpy


def construct_antennas(xyz, diameter, station):
    """
    Construct list of katpoint antenna objects
    based on telescope configuration information.
    For MeerKAT, this is not needed, it is only required for SKA-MID.
    The MID configuration file can be found at:
    https://gitlab.com/ska-telescope/sdp/ska-sdp-datamodels.git
    Use:
    x, y, z, diameter, station =
    numpy.loadtxt('ska1mid.cfg', dtype=object, unpack=True)
    xyz = numpy.column_stack((x, y, z))

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


def construct_target(msname):
    """
    Build katpoint target using optionally source name and
    position.

    :param msname: Measurement set containing visibilities
    :return: Source name and position
    """
    # pylint: disable=import-error,import-outside-toplevel
    from casacore.tables import table

    source_table = table(tablename=f"{msname}/SOURCE")
    source_position = source_table.getcol(columnname="DIRECTION")[0]
    try:
        # Build target
        source_name = source_table.getcol(columnname="NAME")[0]
        cat = katpoint.Catalogue(
            f"{source_name}, radec, {numpy.degrees(source_position[0])}, {numpy.degrees(source_position[1])}"
        )
        target = cat.targets[0]
    except:
        # Build the target with missing source namer
        target = katpoint.construct_radec_target(
            ra=numpy.degrees(source_position[0]),
            dec=numpy.degrees(source_position)[1],
        )

    return target


def convert_coordinates(
    ant,
    beam_center,
    timestamps,
    target_projection,
    target_object,
):
    """
    Calculate (az, el) given a set of information on beam and target.

    :param ant: katpoint antenna object. Either from metadata file,
                Or from config file and created via constructed_antennas
    :param beam_center: Beam centre information (x, y) on the fitting plane
                        x, y are dimensionless
    :param timestamps: numpy array size [ndumps] (from metadata)
    :param target_projection: Name of coordinate system  (from metadata)
    :param target_object: Katpoint target object (from metadata)
    :param target_coord: SkyCoord object that contains RA, Dec information
                         Only used when katpoint target is not provided
    :return: (az, el) coordinates in [nants, 2], radians
    """
    # az_arr = numpy.zeros(len(ants))
    # el_arr = numpy.zeros(len(ants))
    # for i, antenna in enumerate(ants):
    # Convert from (x,y) to (az, el), output in rad
    # Only doing it for a single timestamp at the moment
    az, el = target_object.plane_to_sphere(
        x=beam_center[0],
        y=beam_center[1],
        timestamp=numpy.median(timestamps),
        antenna=ant,
        projection_type=target_projection,
        coord_system="azel",
    )

    return az, el
