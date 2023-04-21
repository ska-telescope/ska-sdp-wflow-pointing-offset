# pylint: disable-msg=too-many-locals
"""
Functions for reading data from Measurement Set
and constructing antenna information.
"""

import logging

import numpy
from rascil.processing_components import create_visibility_from_ms

from ska_sdp_wflow_pointing_offset.utils import construct_antennas

log = logging.getLogger("ska-sdp-pointing-offset")


def _load_ms_tables(msname):
    # pylint: disable=import-outside-toplevel
    """
    Loads Measurement Set.

    :param msname: Measurement set containing visibilities.
    :return: spectral window and pointing sub-table.
    """
    try:
        from casacore.tables import table
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("casacore is not installed") from exc

    spw_table = table(tablename=f"{msname}/SPECTRAL_WINDOW", ack=False)
    pointing_table = table(f"{msname}/POINTING", ack=False)
    return spw_table, pointing_table


def read_visibilities(msname, start_freq=None, end_freq=None):
    """
    Extracts parameters from a measurement set required for
    computing the pointing offsets.

    :param msname: Name of Measurement set file.
    :param start_freq: Starting frequency for selection in MHz.
        If no selection needed, use None
    :param end_freq: Ending frequency for selection in MHz.
        If no selection needed, use None
    :param fit_tovis: Fit primary beam to visibilities instead
        of antenna gains.
    :return: List of Visibility, source_offsets in RA and DEC,
        and list of katpoint Antennas.
    """
    spw_table, pointing_table = _load_ms_tables(msname)

    # Get parameters of interest from the tables
    source_offset = pointing_table.getcol(columnname="SOURCE_OFFSET")
    freqs = (
        numpy.squeeze(spw_table.getcol(columnname="CHAN_FREQ")) / 1.0e6
    )  # Hz -> MHz
    nchan = numpy.squeeze(spw_table.getcol(columnname="NUM_CHAN"))
    if len(freqs) != nchan:
        raise ValueError(
            "Length of frequencies does not match number of channels!"
        )
    if (start_freq and end_freq) is not None:
        # Get the channel numbers matching the start and end frequencies
        for i, frequency in enumerate(freqs):
            if numpy.allclose(frequency, float(start_freq), rtol=1.0e-4):
                chan_low = i
            if numpy.allclose(frequency, float(end_freq), rtol=1.0e-4):
                chan_high = i
        assert (
            numpy.size(chan_low) == numpy.size(chan_high) == 1
        ), "More than one channel cannot have the same frequency!"
        if numpy.all(numpy.isfinite(numpy.r_[chan_low, chan_high])):
            log.info(
                "Channel %s matches input start frequency %s MHz",
                chan_low,
                start_freq,
            )
            log.info(
                "Channel %s matches input end frequency %s MHz",
                chan_high,
                end_freq,
            )
        else:
            raise ValueError(
                "Channel numbers for start and end freq was not found!"
            )
        vis = create_visibility_from_ms(
            msname=msname,
            channum=None,
            start_chan=chan_low,
            end_chan=chan_high,
            ack=False,
            datacolumn="DATA",
            selected_sources=None,
            selected_dds=None,
            average_channels=False,
        )[0]
    else:
        vis = create_visibility_from_ms(
            msname=msname,
            channum=None,
            start_chan=None,
            end_chan=None,
            ack=False,
            datacolumn="DATA",
            selected_sources=None,
            selected_dds=None,
            average_channels=False,
        )[0]

    # Build katpoint Antenna from antenna configuration
    antenna_positions = vis.configuration.data_vars["xyz"].data
    antenna_diameters = vis.configuration.data_vars["diameter"].data
    antenna_names = vis.configuration.data_vars["names"].data
    ants = construct_antennas(
        xyz=antenna_positions,
        diameter=antenna_diameters,
        station=antenna_names,
    )

    return vis, source_offset, ants
