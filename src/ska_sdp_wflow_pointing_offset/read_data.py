# pylint: disable=invalid-name, duplicate-code， too-many-locals

"""
Functions of reading data from MS and RDB file.
"""

from pathlib import Path

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
    except ModuleNotFoundError:
        raise ModuleNotFoundError("casacore is not installed")

    base_table = table(tablename=msname)
    # spw --> spectral window, pol--> polarisation
    spw = table(tablename=f"{msname}/SPECTRAL_WINDOW")
    pol = table(tablename=f"{msname}/POLARIZATION")
    anttab = table(f"{msname}/ANTENNA", ack=False)
    fieldtab = table(f"{msname}/FIELD", ack=False)
    return anttab, base_table, fieldtab, pol, spw


def read_cross_correlation_visibilities(
    msname,
    rfifile=None,
):
    """
    Create a numpy array from a table of a specified MS file.
    This import gain table form calibration table of CASA.

    :param msname: Name of Measurement set file
    :param msname: Name of Rfi mask file

    :return: numpy array

    """

    # Check file exist?
    ms_file = Path(msname)
    if not ms_file.exists():
        return None, None

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
    vis = _base_table.getcol("DATA")
    diam = _ant_table.getcol("DISH_DIAMETER")
    if not all(diam):
        # Note that this must change for SKA as there would be dishes of different sizes
        raise ValueError("Dish diameters must be the same")
    freqs = _spw_table.getcol("CHAN_FREQ") / 1e6  # in MHz

    # source = _field_table.getcol("NAME")[0]
    # nchan = int(_spw_table.getcol("NUM_CHAN"))
    # timestamps = _base_table.getcol("TIME")
    # ants = _ant_table.getcol("STATION")

    # Average over cross-correlations
    avg_vis = numpy.mean(numpy.abs(vis), axis=0)

    # Apply RFI mask
    if rfifile is not None:
        rfi_file_path = Path(rfifile)
        if rfi_file_path.exists():
            with open(rfifile, "rb") as rfi_file:
                rfi_mask = pickle.load(rfi_file)
                filtered_vis = avg_vis[rfi_mask == False, :]
                filtered_freq = numpy.squeeze(freqs)[rfi_mask == False]
                return filtered_vis, filtered_freq

    return avg_vis, freqs


def read_pointing_meta_data_file(rdbfile):
    """
    Read meta-data from RDB file.

    :param rdbname: Name of RDB file

    :return: numpy array
    """
    try:
        import katdal  # pylint: disable=import-error
    except ModuleNotFoundError:
        raise ModuleNotFoundError("katdal is not installed")

    # Check file exist?
    rdb_file = Path(rdbfile)
    if not rdb_file.exists():
        return None

    rdb = katdal.open(rdbfile, chunk_store=None)
    return rdb
