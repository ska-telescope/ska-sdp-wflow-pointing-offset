"""
Main workflow related functions
"""

import numpy as np
import pickle


def apply_rfi_mask(data, freqs, rfi_name=None):
    """
    Apply RFI mask
    :param data: 2D data in [nants, nchan, npol]
    :param freqs: 1D array of frequency [nchan]
    :param rfi_name: Name of the rfi pickle file
    :return: filtered data and freqs array
    """

    rfi_file = open(rfi_name, "rb")
    rfi_mask = pickle.load(rfi_file)
    data = data[:, rfi_mask is False, :]
    freqs = freqs[rfi_mask is False]

    return data, freqs


def select_channels(data, freqs, start_freq, end_freq):
    """
    Select from the visibility data the right channels to look at,
    Inputting starting and end frequency

    :param data: 2D visibility data [nants, nchan, npol]
    :param freqs: 1D frequency array [nchan]
    :param start_freq: Starting frequency (float)
    :param end_freq: Ending frequency (float)
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
    start_freq=None,
    end_freq=None,
    apply_rfi=False,
    rfi_name=None,
    split_pol=False,
):
    """
    Clean visibility data and split into polarisations.

    :param vis_array: Numpy array of visibility data [nants, nchan, npol]
    :param freqs: Numpy array of frequency [nchan]
    :param corr_type: Correlation type
    :param start_freq: Starting frequency for selction
                       If no selection needed, use None
    :param end_freq: Ending frequency for selction
                       If no selection needed, use None
    :param apply_rfi: Apply RFI mask?
    :param rfi_name: Name of RFI mask file
    :param split_pol: Split polarisations?
    :return: numpy array of visibility in [nants]
             If split_pol is True, return each polarisation
             Else return as one array
    """

    # Use amplitude for visibility
    amp_vis = np.abs(vis_array)

    # Apply RFI
    if apply_rfi:
        filtered_vis, filtered_freq = apply_rfi_mask(amp_vis, freqs, rfi_name=rfi_name)

    # Select channels
    if start_freq == None:
        start_freq = freqs[0]
    if end_freq == None:
        end_freq = freqs[-1]
    selected_vis, selected_freq = select_channels(
        filtered_vis, filtered_freq, start_freq, end_freq
    )

    # Average over frequency
    avg_vis = np.mean(selected_vis, axis=1)

    # Split polarisations
    if split_pol:
        if len(corr_type) == 2:
            # (XX,YY) or (RR, LL)
            HH = avg_vis[:, 0]
            VV = avg_vis[:, 1]
        elif len(corr_type) == 4:
            # (XX,XY,YX,YY) or (RR,RL,LR,LL)
            HH = avg_vis[:, 0]
            VV = avg_vis[:, 3]

        return HH, VV

    return avg_vis
