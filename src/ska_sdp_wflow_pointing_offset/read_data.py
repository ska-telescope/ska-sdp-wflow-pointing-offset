# pylint: disable-msg=too-many-locals,too-many-arguments
"""
Functions for reading data from Measurement Set
and constructing antenna information.
"""
import glob
import logging

import katpoint
import numpy
from astropy import units
from astropy.coordinates import SkyCoord
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
        from casacore.tables import table  # pylint: disable=import-error
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("casacore is not installed") from exc

    # Get the spectral window and pointing sub-tables
    spw_table = table(msname + "::SPECTRAL_WINDOW", ack=False)
    pointing_table = table(msname + "::POINTING", ack=False)
    source_table = table(msname + "::SOURCE", ack=False)

    return spw_table, pointing_table, source_table


def _read_visibilities(
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
    :return: List of Visibility, source_offsets in azel, list of
    katpoint Antennas, katpoint target, and source offset timestamps.
    """
    spw_table, pointing_table, source_table = _load_ms_tables(msname)

    # Get the frequencies and source offsets
    requested_azel = pointing_table.getcol("TARGET")

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
        start_chan = channels[0]
        end_chan = channels[-1]

    log.info("Selected channel numbers are %s to %s", start_chan, end_chan)
    vis_list = create_visibility_from_ms(
        msname=msname,
        channum=None,
        start_chan=start_chan,
        end_chan=end_chan,
        ack=False,
        datacolumn="DATA",
        selected_sources=None,
        selected_dds=None,
        average_channels=False,
    )
    vis = vis_list[0]

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

    # Build katpoint Antenna from antenna configuration
    antenna_positions = vis.configuration.data_vars["xyz"].data
    antenna_diameters = vis.configuration.data_vars["diameter"].data
    antenna_names = vis.configuration.data_vars["names"].data
    ants = construct_antennas(
        xyz=antenna_positions,
        diameter=antenna_diameters,
        station=antenna_names,
    )

    source_ra, source_dec = source_table.getcol("DIRECTION")[0]
    target = katpoint.construct_radec_target(ra=source_ra, dec=source_dec)

    source_offset = numpy.zeros((requested_azel.shape[0], len(ants), 2))
    for i, antenna in enumerate(ants):
        # Compute relative azel
        target_azel = numpy.degrees(
            target.azel(numpy.median(offset_timestamps), antenna)
        )
        target_coord = SkyCoord(
            az=target_azel[0] * units.deg,
            alt=target_azel[1] * units.deg,
            frame="altaz",
        )
        requested_coord = SkyCoord(
            az=requested_azel[:, i, 0] * units.deg,
            alt=requested_azel[:, i, 1] * units.deg,
            frame="altaz",
        )

        dazim, delev = target_coord.spherical_offsets_to(requested_coord)
        dazim = dazim.deg
        delev = delev.deg

        relative_azel = numpy.column_stack((dazim, delev))
        source_offset[:, i] = relative_azel

    # Align source_offset and visibility timestamps
    source_offset = interp_timestamps(
        source_offset, offset_timestamps, vis.time.data
    )

    return (
        vis,
        source_offset,
        ants,
        target,
        offset_timestamps,
    )


def read_batch_visibilities(
    msdir,
    apply_mask=False,
    rfi_filename=None,
    start_freq=None,
    end_freq=None,
):
    """
    Extracts parameters from multiple measurement sets required for
        computing the pointing offsets.

    :param msdir: Name of Directory including
        Measurement set file.
    :param apply_mask: Apply RFI mask?
    :param rfi_filename: Name of RFI mask file
    :param start_freq: Starting frequency for selection in MHz.
        If no selection needed, use None
    :param end_freq: Ending frequency for selection in MHz.
        If no selection needed, use None
    :return: List of Visibility, source_offsets in azel, source
        offset timestamps, list of katpoint Antennas, and
        katpoint target.
    """
    vis_list = []
    source_offset_list = []
    offset_timestamps_list = []
    msdir = glob.glob(msdir + "*.ms")
    for msname in sorted(msdir):
        (
            vis,
            source_offset,
            ants,
            target,
            offset_timestamps,
        ) = _read_visibilities(
            msname, apply_mask, rfi_filename, start_freq, end_freq
        )
        vis_list.append(vis)
        source_offset_list.append(source_offset)
        offset_timestamps_list.append(offset_timestamps)

    return (
        vis_list,
        source_offset_list,
        offset_timestamps_list,
        ants,
        target,
    )
