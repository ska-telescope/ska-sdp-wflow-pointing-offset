"""
Optionally applies RFI mask and select frequency ranges
"""

import logging

import numpy

log = logging.getLogger("ska-sdp-pointing-offset")


def apply_rfi_mask(freqs, rfi_filename=None):
    """
    Apply RFI mask.

    :param freqs: 1D array of frequency in Hz [nchan]
    :param rfi_filename: Name of the rfi file (in .txt)
    :return: Filtered frequency and channels array
    """
    rfi_mask = numpy.loadtxt(rfi_filename)
    channels = numpy.array(range(len(freqs)))
    freqs = freqs[rfi_mask == 0]
    channels = channels[rfi_mask == 0]

    return freqs, channels


def select_channels(freqs, channels, start_freq, end_freq):
    """
    Select from the visibility data the desired channels to look at,
    inputting starting and end frequency.
    The function will select the channels between these two frequencies

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
