"""
Functions of reading data from Measurement Set
and Relational Database file.
"""

import katdal  # pylint: disable=import-error
import numpy


def _load_ms_tables(msname):
    # pylint: disable=import-error,import-outside-toplevel
    """
    Load CASA Measurement Set file tables

    :param msname:
    :return:
    """
    try:
        from casacore.tables import table  # pylint: disable=import-error
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("casacore is not installed") from exc

    base_table = table(tablename=msname)
    # spw --> spectral window, pol--> polarisation
    spw = table(tablename=f"{msname}/SPECTRAL_WINDOW")
    pol = table(tablename=f"{msname}/POLARIZATION")
    anttab = table(f"{msname}/ANTENNA", ack=False)
    return anttab, base_table, pol, spw


def read_cross_correlation_visibilities(
    msname,
):
    """
    Create a numpy array from a table of a specified MS file.
    This import gain table form calibration table of CASA.

    :param msname: Name of Measurement set file
    :return: vis, freqs, corr_type
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
    ) = _load_ms_tables(msname)

    # Get parameters of interest from the tables
    vis = base_table.getcol(columnname="DATA")
    diam = ant_table.getcol(columnname="DISH_DIAMETER")
    if not all(diam):
        # Note that this must change for SKA as there would
        # be dishes of different sizes
        raise ValueError("Dish diameters must be the same")
    freqs = spw_table.getcol(columnname="CHAN_FREQ")
    corr_type = numpy.array(
        [
            correlation_products[corr]
            for corr in pol_table.getcol(columnname="CORR_TYPE")
        ]
    )

    return vis, freqs, corr_type


def _open_rdb_file(rdbfile):
    """
    Open a relational database file

    :param rdbfile: file name
    :return: rdb object
    """

    # Check file exist?
    rdb = katdal.open(rdbfile, chunk_store=None)
    return rdb


def read_data_from_rdb_file(rdbfile):
    """
    Read meta-data from RDB file.

    :param rdbname: Name of RDB file
    :return: az, el, timestamps, target projection, ants and target
    """
    rdb = _open_rdb_file(rdbfile)
    rdb.select(scans="track", corrprods="cross")
    ants = rdb.ants
    target = rdb.catalogue.targets[rdb.target_indices[0]]
    return (
        rdb.az,
        rdb.el,
        rdb.timestamps,
        rdb.target_projection,
        ants,
        target,
    )
