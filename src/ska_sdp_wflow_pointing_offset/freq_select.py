"""
Optionally applies RFI mask and select frequency ranges
"""

import logging

import numpy
from ska_sdp_datamodels.visibility.vis_model import Visibility

log = logging.getLogger("ska-sdp-pointing-offset")


def apply_rfi_mask(vis, rfi_filename=None):
    """
    Apply RFI mask.

    :param vis: Visibility containing the observed data_models
    :param rfi_filename: Name of the rfi file (in .txt)
    :return: Visibility containing the observed data_models with
        flagged frequency channels
    """
    # True is flagged channel and False is accepted channel
    freqs = vis.frequency
    try:
        rfi_mask = numpy.loadtxt(rfi_filename)
        if rfi_mask.shape > freqs.shape:
            log.info(
                "Only using the first %i lines of RFI mask", freqs.shape[0]
            )
            rfi_mask = rfi_mask[: freqs.shape[0]]
        elif rfi_mask.shape < freqs.shape:
            log.info(
                "Only apply mask to the first %i channels", rfi_mask.shape[0]
            )
            # Keep the remaining channels by setting their mask to False
            rfi_extended = numpy.zeros(freqs.shape)
            rfi_extended[: rfi_mask.shape[0]] = rfi_mask
            rfi_mask = rfi_extended

        data = vis.vis[:, :, rfi_mask == 0]
        weight = vis.weight[:, :, rfi_mask == 0]
        flags = vis.flags[:, :, rfi_mask == 0]
        freqs = freqs[rfi_mask == 0]
        channel_bandwidth = vis.channel_bandwidth[rfi_mask == 0]

    except FileNotFoundError:
        log.warning(
            "Invalid RFI flagging file provided. No RFI flags applied."
        )

    return Visibility.constructor(
        frequency=freqs.data,
        channel_bandwidth=channel_bandwidth.data,
        phasecentre=vis.phasecentre,
        configuration=vis.configuration,
        uvw=vis.uvw.data,
        time=vis.time.data,
        vis=data.data,
        weight=weight.data,
        integration_time=vis.integration_time.data,
        flags=flags.data,
        baselines=vis.baselines,
        polarisation_frame=vis.visibility_acc.polarisation_frame,
        source=vis.source,
        meta=vis.meta,
    )


def select_channels(vis, start_freq, end_freq):
    """
    Select from the visibility data the desired channels to look at,
    inputting starting and end frequency.
    The function will select the channels between these two frequencies.

    :param vis. Visibility containing the observed data_models with
        optionally flagged frequency channels.
    :param start_freq: Starting frequency in MHz (float)
    :param end_freq: Ending frequency in MHz (float)
    :return: Visibility containing the observed data_models with
        some selected frequencies
    """
    select_mask = (vis.frequency / 1.0e6 > float(start_freq)) & (
        vis.frequency / 1.0e6 < float(end_freq)
    )
    data = vis.vis[:, :, select_mask, :]
    weight = vis.weight[:, :, select_mask, :]
    flags = vis.flags[:, :, select_mask, :]
    freqs = vis.frequency[select_mask]
    channel_bandwidth = vis.channel_bandwidth[select_mask]

    return Visibility.constructor(
        frequency=freqs.data,
        channel_bandwidth=channel_bandwidth.data,
        phasecentre=vis.phasecentre,
        configuration=vis.configuration,
        uvw=vis.uvw.data,
        time=vis.time.data,
        vis=data.data,
        weight=weight.data,
        integration_time=vis.integration_time.data,
        flags=flags.data,
        baselines=vis.baselines,
        polarisation_frame=vis.visibility_acc.polarisation_frame,
        source=vis.source,
        meta=vis.meta,
    )


def clean_vis_data(
    vis,
    start_freq=None,
    end_freq=None,
    apply_mask=False,
    rfi_filename=None,
):
    """
    Clean visibility data and split into polarisations.

    :param vis: Visibility containing the raw observed data_models
    :param start_freq: Starting frequency for selection in MHz.
        If no selection needed, use None
    :param end_freq: Ending frequency for selection in MHz.
        If no selection needed, use None
    :param apply_mask: Apply RFI mask?
    :param rfi_filename: Name of RFI mask file
    :return: Visibility containing the observed data_models with
        optionally flagged and/or some selected frequencies.
    """
    # Apply RFI mask
    if apply_mask:
        vis = apply_rfi_mask(vis, rfi_filename)

    # Optionally select a range of frequencies
    if (start_freq and end_freq) is not None:
        vis = select_channels(vis, start_freq, end_freq)

    return vis
