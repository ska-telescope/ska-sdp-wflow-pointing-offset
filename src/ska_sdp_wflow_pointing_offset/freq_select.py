"""
Optionally applies RFI mask and select frequency ranges
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


def interp_timestamps(origin, ntimes):
    """
    Interpolate timestamps using offset data.

    :param origin: Offset array in [ntimes_origin, nants, 2]
    :param ntimes: Number of timestamps needed for output data
    :return: Offset array in [ntimes, nants, 2]
    """

    def _interp_data(array, new_size):
        """Basic routine to call scipy.interpolate"""
        arr_to_interp = numpy.linspace(-1.0, 1.0, len(array))
        spl = InterpolatedUnivariateSpline(arr_to_interp, array)
        arr_to_fill = numpy.linspace(-1.0, 1.0, new_size)

        return spl(arr_to_fill)

    if origin.ndim != 3 or origin.shape[2] != 2:
        log.warning(
            "Input offset data has the wrong shape, no interpolation done."
        )
        return origin

    direction_az = origin[:, :, 0]
    direction_el = origin[:, :, 1]
    output = numpy.zeros((ntimes, origin.shape[1], 2))
    for i in range(origin.shape[1]):
        az_ant = direction_az[:, i]
        el_ant = direction_el[:, i]
        new_az_ant = _interp_data(az_ant, ntimes)
        new_el_ant = _interp_data(el_ant, ntimes)

        output[:, i, 0] = new_az_ant
        output[:, i, 1] = new_el_ant

    return output
