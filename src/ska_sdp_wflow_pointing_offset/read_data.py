# pylint: disable-msg=too-many-locals
"""
Functions for reading data from Measurement Set.
"""

import numpy

from ska_sdp_wflow_pointing_offset.coord_support import construct_antennas


def _load_ms_tables(msname):
    # pylint: disable=import-error,import-outside-toplevel
    """
    Load CASA Measurement Set file tables

    :param msname: Measurement set containing visibilities
    :return: antenna sub-table, measurement set, pointing
    sub-table, polarisation sub-table, and spectral window
    sub-table.
    """
    try:
        from casacore.tables import table, taql  # pylint: disable=import-error
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("casacore is not installed") from exc

    # Select cross-correlation only
    base_table = table(tablename=msname)
    base_table = taql("select from $base_table where ANTENNA1 != ANTENNA2")

    # spw --> spectral window, pol--> polarisation
    spw = table(tablename=f"{msname}/SPECTRAL_WINDOW")
    anttab = table(f"{msname}/ANTENNA")
    pointing_tab = table(f"{msname}/POINTING")
    pol = table(tablename=f"{msname}/POLARIZATION", ack=False)

    return anttab, base_table, pointing_tab, pol, spw


def read_visibilities(msname):
    """
    Extracts parameters from a measurement set required for
    computing the pointing offsets.

    :param msname: Name of Measurement set file
    :return: visibilities, frequencies, source_offsets in RA
        and DEC, visibility weights, type of correlation
        products, and list of katpoint antennas.
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
        pointing_tab,
        pol_table,
        spw_table,
    ) = _load_ms_tables(msname)

    # Get parameters of interest from the tables
    dish_diam = ant_table.getcol(columnname="DISH_DIAMETER")
    antenna_names = ant_table.getcol(columnname="NAME")
    antenna_positions = ant_table.getcol(columnname="POSITION")
    source_offsets = pointing_tab.getcol(columnname="SOURCE_OFFSET")
    vis = base_table.getcol(columnname="DATA")
    vis_weights = base_table.getcol(columnname="WEIGHT")
    freqs = numpy.squeeze(spw_table.getcol(columnname="CHAN_FREQ"))
    corr_type = numpy.array(
        [
            correlation_products[corr]
            for corr in numpy.squeeze(pol_table.getcol(columnname="CORR_TYPE"))
        ]
    )

    # Build katpoint Antenna
    ants = construct_antennas(
        xyz=antenna_positions, diameter=dish_diam, station=antenna_names
    )

    return vis, freqs, source_offsets, vis_weights, corr_type, ants
