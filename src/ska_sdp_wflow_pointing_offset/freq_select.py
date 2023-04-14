"""
Optionally applies RFI mask and select frequency ranges
"""

import logging

import numpy

log = logging.getLogger("ska-sdp-pointing-offset")


def apply_rfi_mask(vis, rfi_filename=None):
    """
    Apply RFI mask.

    :param vis: Visibility containing the observed data_models
    :param rfi_filename: Name of the rfi file (in .txt)
    :return: filtered data, freqs, and weights array
    """
    # True is flagged channel and False is accepted channel
    freqs = vis.frequency.data
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

        data = vis.vis.data[:, :, rfi_mask == 0]
        freqs = freqs[rfi_mask == 0]
        weights = vis.weight.data[:, :, rfi_mask == 0]

    except FileNotFoundError:
        log.warning(
            "Invalid RFI flagging file provided. No RFI flags applied."
        )

    return data, freqs, weights


def select_channels(data, freqs, weights, start_freq, end_freq):
    """
    Select from the visibility data the desired channels to look at,
    inputting starting and end frequency.
    The function will select the channels between these two frequencies.

    :param data: 4D visibility data [timestamps, ncorr, nchan, npol]
    :param freqs: 1D frequency array in Hz [nchan]
    :param weights: visibility weights in [timestamps, ncorr, nchan, npol]
    :param start_freq: Starting frequency in Hz (float)
    :param end_freq: Ending frequency in Hz (float)
    :return: selected array of (data, freqs)
    """
    select_mask = (freqs > start_freq) & (freqs < end_freq)
    data = data[:, :, select_mask, :]
    weights = weights[:, :, select_mask, :]
    freqs = freqs[select_mask]

    return data, freqs, weights


def clean_vis_data(
    vis,
    start_freq=None,
    end_freq=None,
    apply_mask=False,
    rfi_filename=None,
):
    """
    Clean visibility data and split into polarisations.

    :param vis: Visibility containing the observed data_models
    :param start_freq: Starting frequency for selection in MHz
                       If no selection needed, use None
    :param end_freq: Ending frequency for selection in MHz
                       If no selection needed, use None
    :param apply_mask: Apply RFI mask?
    :param rfi_filename: Name of RFI mask file
    :return: numpy array of visibility with shape [ncorr,]
             If split_pol is True, return each polarisation
             Else return the polarisation-averaged visibilities
    """
    # Apply RFI mask
    if apply_mask:
        filtered_vis, filtered_freqs, filtered_weights = apply_rfi_mask(
            vis, rfi_filename
        )
    else:
        filtered_vis, filtered_freqs, filtered_weights = (
            vis.vis.data,
            vis.frequency.data,
            vis.weight.data,
        )

    # Optionally select a range of frequencies
    if (start_freq and end_freq) is None:
        # No frequency selection is needed
        selected_vis, selected_freqs, selected_weights = (
            filtered_vis,
            filtered_freqs,
            filtered_weights,
        )
    else:
        # Frequency selection is needed
        selected_vis, selected_freqs, selected_weights = select_channels(
            filtered_vis,
            filtered_freqs,
            filtered_weights,
            start_freq,
            end_freq,
        )

    # Average visibilities and weights in frequency
    avg_vis = numpy.mean(selected_vis, axis=2)
    avg_weights = numpy.mean(selected_weights, axis=2)

    # Update the Visibility list for easy reading by RASCIL"s gain solver
    # Check if this really works.
    vis.vis.data = avg_vis
    vis.weight.data = avg_weights
    vis.frequency.data = numpy.mean(selected_freqs)
    vis.channel_bandwidth.data = numpy.mean(vis.channel_bandwidth.data)

    return vis, selected_freqs
