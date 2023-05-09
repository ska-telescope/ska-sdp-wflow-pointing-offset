# pylint: disable-msg=too-many-locals
"""
Functions for reading data from Measurement Set
and constructing antenna information.
"""

import logging

import numpy
from ska_sdp_datamodels.visibility import create_visibility_from_ms
from ska_sdp_datamodels.visibility.vis_model import Visibility

from ska_sdp_wflow_pointing_offset.array_data_func import (
    apply_rfi_mask,
    interp_timestamps,
    select_channels,
)
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

    # Get the spectral window and pointing sub-tables
    spw_table = table(msname + "::SPECTRAL_WINDOW", ack=False)
    pointing_table = table(msname + "::POINTING", ack=False)
    return spw_table, pointing_table


def read_visibilities(
    msname, apply_mask=False, rfi_filename=None, start_freq=None, end_freq=None
):
    """
    Extracts parameters from a measurement set required for
    computing the pointing offsets.

    :param msname: Name of Measurement set file.
    :param apply_mask: Apply RFI mask?
    :param rfi_filename: Name of RFI mask file
    :param start_freq: Starting frequency for selection in MHz.
        If no selection needed, use None
    :param end_freq: Ending frequency for selection in MHz.
        If no selection needed, use None
    :return: List of Visibility, source_offsets in RA and DEC,
        and list of katpoint Antennas.
    """
    spw_table, pointing_table = _load_ms_tables(msname)

    # Get the frequencies and source offsets
    source_offset = pointing_table.getcol("SOURCE_OFFSET")
    offset_timestamps = pointing_table.getcol("TIME")
    freqs = numpy.squeeze(spw_table.getcol("CHAN_FREQ")) / 1.0e6  # Hz -> MHz
    channels = numpy.arange(len(freqs))

    if apply_mask:
        # Apply RFI mask
        freqs, channels = apply_rfi_mask(freqs, rfi_filename)

    # Optionally select frequency channels
    if start_freq is not None and end_freq is not None:
        # Get the channel numbers matching the start and end frequencies
        freqs, channels = select_channels(
            freqs, channels, start_freq, end_freq
        )
        start_chan = channels[0]
        end_chan = channels[-1]
    else:
        if apply_mask:
            start_chan = channels[0]
            end_chan = channels[-1]
        else:
            start_chan = None
            end_chan = None

    log.info("Selected channel numbers are %s to %s", start_chan, end_chan)
    vis = create_visibility_from_ms(
        msname=msname,
        channum=None,
        start_chan=start_chan,
        end_chan=end_chan,
        ack=False,
        datacolumn="DATA",
        selected_sources=None,
        selected_dds=None,
        average_channels=False,
    )[0]

    if apply_mask or (start_freq is not None and end_freq is not None):
        # Update vis to ensure the right frequency range is selected
        # when RFI mask is applied and/or frequency selection is made.
        # This is to overcome the shortcoming of vis containing
        # all data in the provided channel range
        indices = [
            numpy.where(nu == vis.frequency.data / 1.0e6) for nu in freqs
        ]
        indices = [idx[0][0] for idx in indices if idx[0].size > 0]
        vis = Visibility.constructor(
            frequency=freqs * 1.0e6,  # MHz -> Hz
            channel_bandwidth=vis.channel_bandwidth[indices],
            phasecentre=vis.phasecentre,
            configuration=vis.configuration,
            uvw=vis.uvw.data,
            time=vis.time.data,
            vis=vis.vis.data[:, :, indices],
            weight=vis.weight.data[:, :, indices],
            integration_time=vis.integration_time.data,
            flags=vis.flags.data[:, :, indices],
            baselines=vis.baselines,
            polarisation_frame=vis.visibility_acc.polarisation_frame,
            source=vis.source,
            meta=vis.meta,
        )

    # Align timestamps for the source_offset
    source_offset = interp_timestamps(
        source_offset, offset_timestamps, vis.time.data
    )

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
