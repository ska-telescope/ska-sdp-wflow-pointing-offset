# pylint: disable=too-many-locals
"""
Util functions for constructing antenna information
and plotting.
"""
import katpoint
import matplotlib.pyplot as plt
import numpy
import pyuvdata
from astropy.time import Time
from astropy.visualization import time_support
from ska_sdp_func_python.calibration import solve_gaintable


def construct_antennas(xyz, diameter, station):
    """
    Construct list of katpoint antenna objects
    based on telescope configuration information.

    :param xyz: xyz coordinates of antenna positions in [nants, 3]
    :param diameter: Diameter of dishes in [nants]
    :param station: List of the antenna names [nants]
    :return: a set of katpoint.Antenna objects
    """
    latitude, longitude, altitude = pyuvdata.utils.LatLonAlt_from_XYZ(
        xyz=xyz, frame="ITRS", check_acceptability=True
    )
    ants = []
    for ant_name, diam, lat, long, alt in zip(
        station,
        diameter,
        numpy.squeeze(numpy.radians(latitude)),
        numpy.squeeze(numpy.radians(longitude)),
        numpy.squeeze(altitude),
    ):
        # Antenna information
        # The beamwidth is HPBW of an antenna: k * lambda/D
        # We use an estimate of k=1.22 but not used in
        # calculating the beamwidth as k is passed from
        # the command line. The "beamwidth" as used in ant is
        # actually referring to the beamwidth factor, k.
        ant = katpoint.Antenna(
            name=ant_name,
            latitude=lat,
            longitude=long,
            altitude=alt,
            diameter=diam,
            delay_model=None,
            pointing_model=None,
            beamwidth=1.22,
        )
        ants.append(ant)

    return ants


def get_gain_results(gt_list):
    """Get data from a list of GainTables used for plotting.

    :param gt_list: GainTable list to plot

    :return: List of arrays in format of [time, amplitude-1,
    phase-phase(antenna0), residual]

    """

    def angle_wrap(angle):
        if angle > 180.0:
            angle = 360.0 - angle
        if angle < -180.0:
            angle = 360.0 + angle

        return angle

    if not isinstance(gt_list, list):
        gt_list = [gt_list]

    with time_support(format="iso", scale="utc"):
        gains = []
        residual = []
        time = []
        weight = []

        # We only look at the central channel at the moment
        half_of_chans_to_avg = 0
        for gain_table in gt_list:
            time.append(gain_table.time.data[0] / 86400.0)
            current_gain = gain_table.gain.data[0]
            nchan = current_gain.shape[1]
            central_chan = nchan // 2
            gains.append(
                numpy.average(
                    current_gain[
                        :,
                        central_chan
                        - half_of_chans_to_avg:central_chan
                        + half_of_chans_to_avg
                        + 1,
                        0,
                        0,
                    ],
                    axis=1,
                )
            )
            residual.append(
                numpy.average(
                    gain_table.residual.data[
                        0,
                        central_chan
                        - half_of_chans_to_avg:central_chan
                        + half_of_chans_to_avg
                        + 1,
                        0,
                        0,
                    ],
                    axis=0,
                )
            )
            weight.append(
                numpy.average(
                    gain_table.weight.data[
                        0,
                        :,
                        central_chan
                        - half_of_chans_to_avg:central_chan
                        + half_of_chans_to_avg
                        + 1,
                        0,
                        0,
                    ],
                    axis=1,
                )
            )

        gains = numpy.array(gains)
        amp = numpy.abs(gains)
        amp = amp.reshape(amp.shape[1], amp.shape[0])
        phase = numpy.angle(gains, deg=True)
        weight = numpy.array(weight)
        weight = weight.reshape(weight.shape[1], weight.shape[0])

        phase_rel = []
        for i in range(len(phase[0])):
            phase_now = phase[:, i] - phase[:, 0]
            phase_now = [angle_wrap(element) for element in phase_now]
            phase_rel.append(phase_now)
        phase_rel = numpy.array(phase_rel)

        timeseries = Time(time, format="mjd", out_subfmt="str")

        return timeseries, amp, phase_rel, residual, weight


def compute_gains(vis):
    """
    Solves for the antenna gains for the parallel hands only.

    :param vis: Visibility containing the observed data_models
    :return: GainTable containing solution
    """
    gt_list = solve_gaintable(
        vis=vis,
        modelvis=None,
        gain_table=None,
        phase_only=False,
        niter=200,
        tol=1e-06,
        crosspol=False,
        normalise_gains=True,
        jones_type="G",
        timeslice="auto",
    )

    return gt_list


def gt_single_plot(gt_list, plot_name=None):
    """Plot gaintable (gain and residual values) over time
       Used to generate a single plot only

    :param gt_list: GainTable list to plot
    :param plot_name: File name for the plot (contains directory name)

    :return
    """

    if not isinstance(gt_list, list):
        gt_list = [gt_list]

    with time_support(format="iso", scale="utc"):
        timeseries, amp, phase_rel, residual, weight = get_gain_results(
            gt_list=gt_list
        )

        plt.cla()
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(
            4, 1, figsize=(8, 12), sharex=True
        )
        fig.subplots_adjust(hspace=0)

        datetime = gt_list[0]["datetime"][0].data

        for i in range(amp.shape[0]):
            ax1.plot(timeseries, amp[i] - 1, "-", label=f"Antenna {i}")
            ax2.plot(timeseries, phase_rel[i], "-", label=f"Antenna {i}")
            ax3.plot(timeseries, weight[i], "-", label=f"Antenna {i}")

        ax1.ticklabel_format(axis="y", style="scientific", useMathText=True)

        ax1.set_ylabel("Gain Amplitude - 1")
        ax2.set_ylabel("Gain Phase (Antenna - Antenna 0)")
        ax3.set_ylabel("Gain Weight")
        ax3.legend(loc="best")

        ax4.plot(timeseries, residual, "-")
        ax4.set_ylabel("Residual")
        ax4.set_xlabel("Time (UTC)")
        ax4.set_yscale("log")
        plt.xticks(rotation=30)

        fig.suptitle(f"Updated GainTable at {datetime}")
        plt.savefig(plot_name + ".png")


def plot_azel(az_data, el_data):
    """
    Plot az, el for visual examination.

    :param az_data: Azimuth values of observation.
    :param el_data: Elevation values of observation.
    :return Plot of elevation vs azimuth
    """

    plt.figure(figsize=(10, 5))
    plt.plot(az_data, el_data, "bo")
    plt.xlabel("Azimuth [degrees]")
    plt.ylabel("Elevation [degrees]")
    plt.savefig("az_el_plot.png")
