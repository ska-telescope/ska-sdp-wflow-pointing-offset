"""
Functions of reading data from Measurement Set
and Relational Database file.
"""

import katdal  # pylint: disable=import-error
import katpoint
import numpy


def _load_ms_tables(msname, auto=False):
    # pylint: disable=import-error,import-outside-toplevel
    """
    Load CASA Measurement Set file tables

    :param msname: Measurement set containing visibilities
    :param auto: Read auto-correlation visibilities?
    :return: antenna sub-table, measurement set, polarisation
    sub-table, and spectral window sub-table, and source sub-table.
    """
    try:
        from casacore.tables import table, taql  # pylint: disable=import-error
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("casacore is not installed") from exc

    base_table = table(tablename=msname)
    if auto:
        # Select auto-correlation only
        base_table = taql("select from $base_table where ANTENNA1 == ANTENNA2")
    else:
        # Select cross-correlation only
        base_table = taql("select from $base_table where ANTENNA1 != ANTENNA2")

    # spw --> spectral window, pol--> polarisation
    spw = table(tablename=f"{msname}/SPECTRAL_WINDOW")
    pol = table(tablename=f"{msname}/POLARIZATION")
    anttab = table(f"{msname}/ANTENNA", ack=False)
    source_table = table(tablename=f"{msname}/SOURCE", ack=False)

    return anttab, base_table, pol, spw, source_table


def read_visibilities(msname, auto=False):
    """
    Create a numpy array from a table of a specified MS file.
    This import gain table form calibration table of CASA.

    :param msname: Name of Measurement set file
    :param auto: Read auto-correlation visibilities?
    :return: visibilities, frequencies, type of correlation products,
    dish diameter, visibility weights, and katpoint target.
    """

    # The following keys match the polarisation IDs
    # from the casa MS file
    correlation_products = {
        5: "RR",
        6: "RL",
        7: "LR",
        8: "LL",
        9: "XX",
        10: "XY",
        11: "YX",
        12: "YY",
    }

    (
        ant_table,
        base_table,
        pol_table,
        spw_table,
        source_table,
    ) = _load_ms_tables(msname, auto)

    # Get parameters of interest from the tables
    dish_diam = ant_table.getcol(columnname="DISH_DIAMETER")
    if not all(dish_diam):
        # Note that this must change for SKA as there would
        # be dishes of different sizes
        raise ValueError("Dish diameters must be the same")
    vis = base_table.getcol(columnname="DATA")
    vis_weight = base_table.getcol(columnname="WEIGHT")
    freqs = numpy.squeeze(spw_table.getcol(columnname="CHAN_FREQ"))
    corr_type = numpy.array(
        [
            correlation_products[corr]
            for corr in numpy.squeeze(pol_table.getcol(columnname="CORR_TYPE"))
        ]
    )

    # Build katpoint target
    source_position = source_table.getcol(columnname="DIRECTION")[0]
    try:
        # When target's name is known
        source_name = source_table.getcol(columnname="NAME")[0]
        cat = katpoint.Catalogue(
            f"{source_name}, radec, "
            f"{numpy.degrees(source_position[0])}, "
            f"{numpy.degrees(source_position[1])}"
        )
        target = cat.targets[0]
    except RuntimeError:
        # When target's name is unknown
        target = katpoint.construct_radec_target(
            ra=numpy.degrees(source_position[0]),
            dec=numpy.degrees(source_position)[1],
        )

    return vis, freqs, corr_type, dish_diam[0], vis_weight, target


def _open_rdb_file(rdbfile):
    """
    Open a relational database file

    :param rdbfile: file name
    :return: rdb object
    """

    # Check file exist?
    rdb = katdal.open(rdbfile, chunk_store=None)
    return rdb


def read_data_from_rdb_file(rdbfile, auto=False):
    """
    Read meta-data from RDB file.

    :param rdbname: Name of RDB file
    :return: az, el, timestamps, target projection, ants, and
    target coordinates of the dish in radians. The target
    coordinates with shape (2, number of timestamps, number of
    antennas) are projections of the spherical coordinates
    of the dish pointing direction to a plane with the target
    position at the origin.
    """
    rdb = _open_rdb_file(rdbfile)
    if auto:
        corrprods = "auto"
    else:
        corrprods = "cross"
    rdb.select(scans="track", corrprods=corrprods)
    ants = rdb.ants

    return (
        rdb.timestamps,
        rdb.target_projection,
        ants,
        numpy.array([rdb.target_x, rdb.target_y]),
    )
