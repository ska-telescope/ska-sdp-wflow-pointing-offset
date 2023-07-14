# pylint: disable=too-many-locals
"""
Functions for manipulation of data that are numpy arrays.
Currently contains:
1. Applying RFI mask and select frequency ranges for input data
2. Aligning pointing and visibility timestamps via interpolation
3. Time-averaging of visibility or gain amplitudes and weights
4. Solves for complex un-normalised antenna gains (G terms)
5. Weighted-average of the fitted pointing offsets
6. Extracts visibility or gain amplitudes per scan and optionally
per frequency chunk (when fitting to gains) required for the
fitting
"""

import logging

import numpy
from katpoint import wrap_angle
from scipy.interpolate import NearestNDInterpolator
from ska_sdp_datamodels.visibility import Visibility
from ska_sdp_func_python.calibration import solve_gaintable

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
                      From Visibility
    :return: Offset array in [ntimes_new, nants, 2]
    """

    if origin_data.ndim != 3 or origin_data.shape[2] != 2:
        log.warning(
            "Input offset data has the wrong shape, no interpolation done."
        )
        return origin_data

    ntimes_new = new_times.shape[0]

    sort_index = numpy.argsort(origin_times)
    origin_times = origin_times[sort_index]
    origin_data = origin_data[sort_index]

    direction_az = origin_data[:, :, 0]
    direction_el = origin_data[:, :, 1]
    output = numpy.zeros((ntimes_new, origin_data.shape[1], 2))

    times = numpy.array([origin_times, new_times]).T
    for i in range(origin_data.shape[1]):
        az_ant = direction_az[:, i]
        el_ant = direction_el[:, i]

        interp_az = NearestNDInterpolator(x=times, y=az_ant)
        interp_el = NearestNDInterpolator(x=times, y=el_ant)

        output[:, i, 0] = interp_az.values
        output[:, i, 1] = interp_el.values

    return output


def _compute_gains(vis, num_chunks):
    """
    Solves for the antenna gains for the parallel hands only.

    :param vis: The observed Visibility object
    :param num_chunks: Number of frequency chunks (integer)

    :return: GainTable containing solution
    """
    freqs = vis.frequency.data
    if num_chunks > 1:
        try:
            channels = numpy.arange(len(freqs)).reshape(num_chunks, -1)
        except ValueError:
            log.warning(
                "Frequency channels not divisible by number of chunks. "
                "Using num_chunks=1 instead."
            )
            gt_list = [
                solve_gaintable(
                    vis=vis,
                    modelvis=None,
                    gain_table=None,
                    phase_only=False,
                    niter=200,
                    tol=1e-06,
                    crosspol=False,
                    normalise_gains=None,
                    jones_type="G",
                    timeslice=None,
                )
            ]
        else:
            gt_list = []
            for chan in channels:
                start = chan[0]
                end = chan[-1] + 1
                new_vis = Visibility.constructor(
                    frequency=freqs[start:end],
                    channel_bandwidth=vis.channel_bandwidth.data[start:end],
                    phasecentre=vis.phasecentre,
                    baselines=vis["baselines"],
                    configuration=vis.attrs["configuration"],
                    uvw=vis["uvw"].data,
                    time=vis["time"].data,
                    vis=vis.vis.data[:, :, start:end, :],
                    flags=vis.flags.data[:, :, start:end, :],
                    weight=vis.weight.data[:, :, start:end, :],
                    integration_time=vis["integration_time"].data,
                    polarisation_frame=vis.visibility_acc.polarisation_frame,
                    source=vis.attrs["source"],
                    meta=vis.attrs["meta"],
                )
                gt_list.append(
                    solve_gaintable(
                        vis=new_vis,
                        modelvis=None,
                        gain_table=None,
                        phase_only=False,
                        niter=200,
                        tol=1e-06,
                        crosspol=False,
                        normalise_gains=None,
                        jones_type="G",
                        timeslice=None,
                    )
                )
    else:
        gt_list = [
            solve_gaintable(
                vis=vis,
                modelvis=None,
                gain_table=None,
                phase_only=False,
                niter=200,
                tol=1e-06,
                crosspol=False,
                normalise_gains=None,
                jones_type="G",
                timeslice=None,
            )
        ]

    return gt_list


def _time_avg_amp(data, time_avg=None):
    """
    Perform no, median, or mean averaging of the visibility or
    gain amplitudes, or weights in time. No averaging means select the
    visibility or gain amplitudes at the first timestamp.

    :param data: Visibility or gain amplitudes in [ntimes, nants]
    :param time_avg: Type of averaging [None, "median", "mean"]
    :return: Time-average visibility or gain amplitudes [nants]
    """
    if time_avg is None:
        # Select vis or gain amplitudes at first timestamp
        data = data[
            0,
        ]
    elif time_avg == "median":
        # Median average
        data = numpy.median(data, axis=0)
    elif time_avg == "mean":
        # Mean average
        data = data.mean(axis=0)
    else:
        log.warning("Averaging type unknown. Using no averaging!")
        # Select vis or gain amplitudes at first timestamp
        data = data[
            0,
        ]

    return data


def _get_autocorrelations(vis):
    """
    Extracts the autocorrelation visibilities and their weights
    from visibilities containing both auto and cross-correlations.
    Translates the visibilities and weights from (ntimes, nbaselines,
    nfreqs, npols) to (ntimes, nants, nfreqs, npols)

    :param vis: Visibility object
    :return: visibility amplitude and its weights
    """
    get_autocorr = vis.antenna1.data == vis.antenna2.data
    vis_weights = vis.weight.data[:, get_autocorr, :, :]
    vis = vis.vis.data[:, get_autocorr, :, :]

    if vis.shape[3] == 2:
        log.info("Found two polarisations...")
    elif vis.shape[3] == 4:
        log.info(
            "Found four polarisations. Extracting the "
            "parallel hand polarisations..."
        )
        # Polarisations are (XX, XY, YX, YY) or (RR, RL, LR, LL)
        vis = numpy.moveaxis(
            numpy.array((vis[:, :, :, 0], vis[:, :, :, 3])), 0, 3
        )
        vis_weights = numpy.moveaxis(
            numpy.array((vis_weights[:, :, :, 0], vis_weights[:, :, :, 3])),
            0,
            3,
        )
    else:
        raise ValueError("Polarisation type not supported!")

    return numpy.abs(vis), vis_weights


class ExtractPerScan:
    """
    Extracts the visibility or gain amplitude and the antenna pointings
    for each scan required for the beam fitting routine.

    :param vis_list: List of Visibility object
    :param source_offset_list: List of source_offset in azel coordinates
    :param ants: List of katpoint Antennas
    :param time_avg: Type of visibility or gain amplitude averaging. Options
        are None, "median", "mean"]
    """

    def __init__(self, vis_list, source_offset_list, ants, time_avg):
        self.vis_list = vis_list
        self.source_offset_list = source_offset_list
        self.ants = ants
        self.time_avg = time_avg
        self.x_per_scan = numpy.zeros(
            (len(self.source_offset_list), len(self.ants), 2)
        )
        for scan, source_offset in enumerate(self.source_offset_list):
            # Average antenna pointings in time
            self.x_per_scan[scan] = source_offset.mean(axis=0)

    def from_vis(self):
        """
        Extracts the visibility amplitude for each scan required for
        the beam fitting routine. A placeholder for ORC-1572 which
        would investigate in detail the option of fitting the primary
        beams to the auto-correlation visibility amplitudes of each
        antenna

        :return: source offset per scan, visibility amplitude per scan,
        weights_per_scan, and frequencies of observation
        """
        freqs = 0.0
        y_per_scan = numpy.zeros((len(self.ants), len(self.vis_list)))
        weights_per_scan = numpy.zeros((len(self.ants), len(self.vis_list)))
        for scan, vis in enumerate(self.vis_list):
            # Get autocorrelations visibility amplitudes
            vis_amp, vis_weights = _get_autocorrelations(vis)

            # No or time-averaging of visibility amplitudes after
            # averaging in frequency and polarisation
            vis_amp = _time_avg_amp(vis_amp.mean(axis=(2, 3)), self.time_avg)
            vis_weights = _time_avg_amp(
                vis_weights.mean(axis=(2, 3)), self.time_avg
            )
            if scan == 0:
                # We want to use the frequency at the higher end of the
                # frequency for better pointing accuracy
                freqs = numpy.squeeze(vis.frequency.data[-1])
            y_per_scan[:, scan] = vis_amp
            weights_per_scan[:, scan] = vis_weights

        return self.x_per_scan, y_per_scan, weights_per_scan, freqs

    def from_gains(self, num_chunks):
        """
        Extracts the gain amplitude for each scan required for the
        beam fitting routine.

        :param num_chunks: Number of frequency chunks for gain
            calibration

        :return source offset per scan, gain amplitudes per scan,
        weights_per_scan, and frequencies of observation
        """
        # Solve for the un-normalised G terms for each scan
        if num_chunks > 1:
            freqs = numpy.zeros(num_chunks)
            y_per_scan = numpy.zeros(
                (len(self.ants), num_chunks, len(self.vis_list))
            )
            weights_per_scan = numpy.zeros(
                (len(self.ants), num_chunks, len(self.vis_list))
            )
            for scan, vis in enumerate(self.vis_list):
                log.info(
                    "Solving for the antenna complex gains for Scan %d",
                    scan + 1,
                )
                gt_list = _compute_gains(vis, num_chunks)
                for chunk in range(num_chunks):
                    # Gains have shape (ntimes, nants, nfreqs,
                    # receptor1, receptor2)
                    gt_amp = numpy.abs(gt_list[chunk].gain.data)
                    gt_amp = numpy.dstack(
                        (gt_amp[:, :, :, 0, 0], gt_amp[:, :, :, 1, 1])
                    )
                    gt_weights = gt_list[0].weight.data
                    gt_weights = numpy.dstack(
                        (
                            gt_weights[:, :, :, 0, 0],
                            gt_weights[:, :, :, 1, 1],
                        )
                    )

                    # Perform no or time-averaging of gain amplitudes
                    # and weights after averaging in polarisation
                    gt_amp = _time_avg_amp(gt_amp.mean(axis=2), self.time_avg)
                    gt_weights = _time_avg_amp(
                        gt_weights.mean(axis=2), self.time_avg
                    )

                    freqs[chunk] = numpy.squeeze(gt_list[chunk].frequency.data)
                    y_per_scan[:, chunk, scan] = gt_amp
                    weights_per_scan[:, chunk, scan] = gt_weights
        else:
            freqs = 0.0
            y_per_scan = numpy.zeros((len(self.ants), len(self.vis_list)))
            weights_per_scan = numpy.zeros(
                (len(self.ants), len(self.vis_list))
            )
            for scan, vis in enumerate(self.vis_list):
                log.info(
                    "Solving for the antenna complex gains for scan %d",
                    scan + 1,
                )
                gt_list = _compute_gains(vis, 1)

                # Gains have shape (ntimes, nants, nfreqs,
                # receptor1, receptor2)
                gt_amp = numpy.abs(gt_list[0].gain.data)
                gt_amp = numpy.dstack(
                    (gt_amp[:, :, :, 0, 0], gt_amp[:, :, :, 1, 1])
                )
                gt_weights = gt_list[0].weight.data
                gt_weights = numpy.dstack(
                    (gt_weights[:, :, :, 0, 0], gt_weights[:, :, :, 1, 1])
                )

                # Average in polarisation
                gt_amp = gt_amp.mean(axis=2)
                gt_weights = gt_weights.mean(axis=2)

                # Perform no or time-averaging of gain amplitudes and weights
                gt_amp = _time_avg_amp(gt_amp, self.time_avg)
                gt_weights = _time_avg_amp(gt_weights, self.time_avg)

                if scan == 0:
                    freqs = numpy.squeeze(gt_list[0].frequency.data)
                y_per_scan[:, scan] = gt_amp
                weights_per_scan[:, scan] = gt_weights

        return self.x_per_scan, y_per_scan, weights_per_scan, freqs


def weighted_average(
    ants,
    fitted_beams,
    target,
    offset_timestamps,
    num_chunks,
):
    """
    Compute the weighted average of the fitted pointing offsets

    :param ants: List of katpoint antennas
    :param fitted_beams: A dictionary of the fitted beams
    :param target: katpoint target
    :param offset_timestamps: Source offset timestamps
    :param num_chunks: Number of frequency chunks for gain
        calibration if fitting primary beams to gain amplitudes
    :return: The weighted average of the valid fitted AzEl offsets
        and the cross-elevation offset in arcminutes for each antenna
    """

    azel_offset = numpy.full((len(ants), 2), numpy.nan)
    cross_el_offset = numpy.full(len(ants), numpy.nan)
    antenna_names = []
    for i, antenna in enumerate(ants):
        antenna_names.append(antenna.name)
        beams_freq = fitted_beams.get(antenna.name, [])
        if num_chunks > 1:
            beams_freq = [
                b for b in beams_freq if b is not None and b.is_valid
            ]
            if not beams_freq:
                log.warning(
                    "%s had no valid primary beam fitted", antenna.name
                )
                continue
            offsets_freq = numpy.array([b.centre for b in beams_freq])
            offsets_freq_std = numpy.array([b.std_centre for b in beams_freq])
            weights_freq = 1.0 / offsets_freq_std**2

            # Do weighted average of offsets over frequency chunks
            results = numpy.average(
                offsets_freq, axis=0, weights=weights_freq, returned=True
            )
            pointing_offset = results[0]
        else:
            if beams_freq is not None and beams_freq.is_valid:
                pointing_offset = numpy.array(beams_freq.centre)
            else:
                log.warning(
                    "%s had no valid primary beam fitted", antenna.name
                )
                continue

        # Compute cross-elevation offset as azimuth offset * cosine (el). We
        # use the target elevation as the elevation
        pointing_offset = wrap_angle(numpy.radians(pointing_offset))
        target_azel = numpy.array(
            target.azel(
                timestamp=numpy.median(offset_timestamps), antenna=antenna
            )
        )
        target_azel = numpy.degrees(wrap_angle(target_azel))
        x_el_offset = pointing_offset[0] * numpy.cos(
            numpy.radians(target_azel[1])
        )

        azel_offset[i] = numpy.degrees(pointing_offset) * 60.0
        cross_el_offset[i] = numpy.degrees(x_el_offset) * 60.0

    output_offset = numpy.column_stack(
        (antenna_names, azel_offset[:, 0], azel_offset[:, 1], cross_el_offset)
    )

    return output_offset
