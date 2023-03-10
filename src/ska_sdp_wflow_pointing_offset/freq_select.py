# pylint: disable=too-many-arguments, too-many-locals
"""
Optionally applies RFI mask and select frequency ranges
"""

import pickle

import numpy


def apply_rfi_mask(data, freqs, rfi_filename=None):
    """
    Apply RFI mask.
    :param data: 3D data in [ncorr, nchan, npol]
    :param freqs: 1D array of frequency in Hz [nchan]
    :param rfi_filename: Name of the rfi pickle file
    :return: filtered data and freqs array
    """
    # True is flagged channel and False is accepted channel
    with open(rfi_filename, "rb") as rfi_file:
        rfi_mask = pickle.load(rfi_file)
        data = data[:, rfi_mask == 0]
        freqs = freqs[rfi_mask == 0]

    return data, freqs


def select_channels(data, freqs, start_freq, end_freq):
    """
    Select from the visibility data the right channels to look at,
    inputting starting and end frequency.
    The function will select the channels between these two frequencies

    :param data: 3D visibility data [ncorr, nchan, numpyol]
    :param freqs: 1D frequency array in Hz [nchan]
    :param start_freq: Starting frequency in Hz (float)
    :param end_freq: Ending frequency in Hz (float)
    :return: selected array of (data, freqs)
    """
    select_mask = (freqs > start_freq) & (freqs < end_freq)
    data = data[:, select_mask, :]
    freqs = freqs[select_mask]

    return data, freqs


def clean_vis_data(
    vis_array,
    freqs,
    corr_type,
    vis_weight,
    start_freq=None,
    end_freq=None,
    apply_mask=False,
    rfi_filename=None,
):
    """
    Clean visibility data and split into polarisations.

    :param vis_array: Numpy array of visibility data [ncorr, nchan, npol]
    :param freqs: Numpy array of frequency [nchan]
    :param corr_type: Correlation type e.g. (XX,YY), (RR, LL),
                        (XX,XY,YX,YY) or (RR,RL,LR,LL)
    :param vis_weight: Weights of the visibilities [ncorr, npol]
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

    # Use amplitude for visibility
    amp_vis = numpy.abs(vis_array)

    # Apply RFI
    if apply_mask:
        filtered_vis, filtered_freq = apply_rfi_mask(
            amp_vis, freqs, rfi_filename
        )
    else:
        filtered_vis, filtered_freq = amp_vis, freqs

    # Optionally select a range of frequencies
    if (start_freq and end_freq) is None:
        # No frequency selection is needed
        selected_vis, selected_freq = filtered_vis, filtered_freq
    else:
        # Frequency selection is needed
        selected_vis, selected_freq = select_channels(
            filtered_vis, filtered_freq, start_freq, end_freq
        )

    # Average over frequency and split visibilities, weights,
    # and correlation type into the parallel hands
    avg_vis = numpy.mean(selected_vis, axis=1)
    if len(corr_type) == 2:
        # (XX,YY) or (RR, LL)
        corr_type = [corr_type[0], corr_type[1]]
        vis_h = avg_vis[:, 0]
        vis_v = avg_vis[:, 1]
        weight_h = vis_weight[:, 0]
        weight_v = vis_weight[:, 1]
    elif len(corr_type) == 4:
        # (XX,XY,YX,YY) or (RR,RL,LR,LL)
        corr_type = [corr_type[0], corr_type[3]]
        vis_h = avg_vis[:, 0]
        vis_v = avg_vis[:, 3]
        weight_h = vis_weight[:, 0]
        weight_v = vis_weight[:, 3]
    else:
        raise ValueError("Polarisation type not supported")

    return numpy.array(
        [[vis_h, vis_v], selected_freq, [weight_h, weight_v], corr_type]
    )
