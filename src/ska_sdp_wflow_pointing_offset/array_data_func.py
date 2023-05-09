"""
Functions for manipulation of data that are numpy arrays.
Currently contains:
1. Applying RFI mask and select frequency ranges for input data
2. Interpolate timestamps for source offset data
"""

import logging

import numpy
from scipy.interpolate import InterpolatedUnivariateSpline

log = logging.getLogger("ska-sdp-pointing-offset")


def apply_rfi_mask(freqs, rfi_filename):
    """
    Apply RFI mask.

    :param freqs: 1D array of frequency in Hz [nchan]
    :param rfi_filename: Name of the rfi file (in .txt)
    :return: Filtered frequency and channels array
    """
    channels = numpy.arange(len(freqs))
    try:
        rfi_mask = numpy.loadtxt(rfi_filename)
        freqs = freqs[rfi_mask == 0]
        channels = channels[rfi_mask == 0]
    except FileNotFoundError:
        log.info("Invalid RFI flagging file provided. No RFI flags applied.")

    return freqs, channels


def select_channels(freqs, channels, start_freq, end_freq):
    """
    Select the desired frequencies and corresponding channels
    of interest by inputting the start and end frequency. The
    function will select the channels between these two
    frequencies.

    :param freqs: 1D frequency array in MHz [nchan]
    :param channels: 1D frequency channels
    :param start_freq: Starting frequency in MHz (float)
    :param end_freq: Ending frequency in MHz (float)
    :return: selected array of (frequencies, channels)
    """
    select_mask = (freqs > float(start_freq)) & (freqs < float(end_freq))
    freqs = freqs[select_mask]
    channels = channels[select_mask]

    return freqs, channels


def interp_timestamps(origin_data, origin_times, new_times):
    """
    Interpolate timestamps using offset data.

    :param origin_data: Offset array in [ntimes_origin, nants, 2]
    :param origin_times: Original times information [ntimes_origin]
    :param new_times: New times information [ntimes_new]
                      From Visibility or gains
    :return: Offset array in [ntimes_new, nants, 2]
    """

    if origin_data.ndim != 3 or origin_data.shape[2] != 2:
        log.warning(
            "Input offset data has the wrong shape, no interpolation done."
        )
        return origin_data

    ntimes_new = new_times.shape[0]

    direction_az = origin_data[:, :, 0]
    direction_el = origin_data[:, :, 1]
    output = numpy.zeros((ntimes_new, origin_data.shape[1], 2))
    for i in range(origin_data.shape[1]):
        az_ant = direction_az[:, i]
        el_ant = direction_el[:, i]

        spl_az = InterpolatedUnivariateSpline(origin_times, az_ant)
        new_az_ant = spl_az(new_times)
        spl_el = InterpolatedUnivariateSpline(origin_times, el_ant)
        new_el_ant = spl_el(new_times)

        output[:, i, 0] = new_az_ant
        output[:, i, 1] = new_el_ant

    return output
