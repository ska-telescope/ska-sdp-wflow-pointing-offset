"""
Main workflow related functions
"""

import numpy as np
import pickle


def apply_rfi_mask(data, freqs, rfi_name=None):
    """
    Apply RFI mask
    :param data: 2D data in [nchan, npol]
    :param freqs: 1D array of frequency [nchan]
    :param rfi_name: Name of the rfi pickle file
    :return: filtered data and freqs array
    """

    rfi_file = open(rfi_name, "rb")
    rfi_mask = pickle.load(rfi_file)
    print(rfi_mask.shape)
    data = data[rfi_mask == False, :]
    freqs = freqs[rfi_mask == False]

    return data, freqs


def select_channels(data, freqs, start_freq, end_freq):
    """
    Select from the visibility data the right channels to look at,
    Inputting starting and end frequency

    :param data: 2D visibility data [nchan, npol]
    :param freqs: 1D frequency array [nchan]
    :param start_freq: Starting frequency
    :param end_freq: Ending frequency
    :return: selected array of (data, freqs)
    """
    select_mask = (freqs > start_freq) & (freqs < end_freq)
    data = data[select_mask, :]
    freqs = freqs[select_mask]

    return data, freqs


def clean_vis_data(
    vis_array,
    freqs,
    corr_type,
    start_freq=None,
    end_freq=None,
    apply_rfi=False,
    rfi_name=None,
    split_pol=False,
):
    """
    Clean visibility data and split into polarisations
    :param vis_array: Numpy array of visibility data [ncorr, nchan, npol]
    :param freqs: Numpy array of frequency [nchan, 1]
    :param corr_type: Correlation type
    :param start_freq: Starting frequency for selction
                       If no selection needed, use None
    :param end_freq: Ending frequency for selction
                       If no selection needed, use None
    :param apply_rfi: Apply RFI mask?
    :param rfi_name: Name of RFI mask file
    :param split_pol: Split polarisations?
    :return:
    """

    # Average over cross-correlations
    avg_vis = np.mean(np.abs(vis_array), axis=0)
    freqs = np.squeeze(freqs)

    # Apply RFI
    if apply_rfi:
        filtered_vis, filtered_freq = apply_rfi_mask(avg_vis, freqs, rfi_name=rfi_name)

    # Select channels
    if start_freq == None:
        start_freq = freqs[0]
    if end_freq == None:
        end_freq = freqs[-1]
    selected_vis, selected_freq = select_channels(
        filtered_vis, filtered_freq, start_freq, end_freq
    )

    # Split polarisations
    if split_pol:
        if len(corr_type) == 2:
            # (XX,YY) or (RR, LL)
            HH = selected_vis[:, 0]
            VV = selected_vis[:, 1]
        elif len(corr_type) == 4:
            # (XX,XY,YX,YY) or (RR,RL,LR,LL)
            HH = selected_vis[:, 0]
            VV = selected_vis[:, 3]

        return selected_freq, HH, VV

    return selected_freq, selected_vis
