# pylint: disable=invalid-name, duplicate-code， too-many-locals

"""
Functions of reading data from MS and RDB file.
"""

import re

import katdal  # pylint: disable=import-error
import numpy


def _load_ms_tables(msname):
    # pylint: disable=import-error,import-outside-toplevel
    """
    Load casa MS file tables

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
    fieldtab = table(f"{msname}/FIELD", ack=False)
    return anttab, base_table, fieldtab, pol, spw


def read_cross_correlation_visibilities(
    msname,
):
    """
    Create a numpy array from a table of a specified MS file.
    This import gain table form calibration table of CASA.

    :param msname: Name of Measurement set file

    :return: numpy array

    """

    # Check file exist?
    # ms_file = Path(msname)
    # if not ms_file.exists():
    #     return None, None

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
        _ant_table,
        _base_table,
        _fieldtab,
        _pol_table,
        _spw_table,
    ) = _load_ms_tables(msname)

    # Get parameters of interest from the tables
    vis = _base_table.getcol(columnname="DATA")
    diam = _ant_table.getcol(columnname="DISH_DIAMETER")
    if not all(diam):
        # Note that this must change for SKA as there would
        # be dishes of different sizes
        raise ValueError("Dish diameters must be the same")
    freqs = _spw_table.getcol(columnname="CHAN_FREQ") / 1e6  # in MHz

    # source = _field_table.getcol(columnname="NAME")[0]
    # nchan = int(_spw_table.getcol(columnname="NUM_CHAN"))
    # timestamps = _base_table.getcol(columnname="TIME")
    # ants = _ant_table.getcol(columnname="STATION")
    corr_type = numpy.array(
        [
            correlation_products[corr]
            for corr in _pol_table.getcol(columnname="CORR_TYPE")
        ]
    )

    return vis, freqs, corr_type


def _open_rdb_file(rdbfile):
    """
    Open a rdb file

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
    :return: numpy array
    """
    _rdb = _open_rdb_file(rdbfile)
    _rdb.select(scans="track", corrprods="cross")
    ants = _rdb.ants
    target = _rdb.catalogue.targets[_rdb.target_indices[0]]
    return (
        _rdb.az,
        _rdb.el,
        _rdb.timestamps,
        _rdb.target_projection,
        ants,
        target,
    )


def read_pointing_meta_data_file(rdbfile):
    """
    Read meta-data from RDB file.

    :param rdbname: Name of RDB file
    :return: numpy array
    """
    _rdb = _open_rdb_file(rdbfile)
    logs = _rdb.obs_script_log
    ant = []
    azel = []
    for line in logs:
        result = re.findall(
            r"""
(INFO|WARNING)\s+([a-z]+[0-9]+)\s+(\([\+|\-?][0-9]+\.[0-9]+, [0-9]+\.[0-9]+\)|)
""",
            line,
        )
        if len(result) > 0:
            ant.append(result[0][1])
            if result[0][0] == "INFO":
                azel_tmp = re.split(r"[(,\s)]\s*", result[0][2])
                azel.append([float(azel_tmp[1]), float(azel_tmp[2])])
            else:
                azel.append([999.99, 99.99])
    return numpy.array(azel)
