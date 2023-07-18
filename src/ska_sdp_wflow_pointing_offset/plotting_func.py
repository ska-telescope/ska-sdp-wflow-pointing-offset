"""
Functions for plotting and visualisation of outputs
"""

import logging

import matplotlib.pyplot as plt
import numpy

log = logging.getLogger("ska-sdp-pointing-offset")


def plot_offsets(azel_offset, cross_el_offset, prefix="test"):
    """
    Direct scatter plot of offset outputs for a single antenna.
    The information are in save_offsets.txt
    Top panel: El offset - Az offset
    Bottom panel: El offset - cross_el offet

    :param azel_offset: Offset array in arcminutes (contains az, el)
    :param cross_el_offset: Cross_el offset array in arcminutes
    :param prefix: Unique plot name prefix (e.g. Meerkat)
    """
    fig, [ax1, ax2] = plt.subplots(2, 1, sharex=True)
    ax1.scatter(azel_offset[:, 1], azel_offset[:, 0], c="r")
    ax1.set_title("Az-El Offset")
    ax1.set_ylabel("Azimuth (arcmin)")

    ax2.scatter(azel_offset[:, 1], cross_el_offset, c="b")
    ax2.set_title("Elevation - Cross Elevation")
    ax2.set_ylabel("Cross elevation (acrmin)")
    ax2.set_xlabel("Elevation (arcmin)")

    ax2.yaxis.set_label_position("right")
    ax2.yaxis.tick_right()

    plt.savefig(prefix + "_azel_offset.png")
    plt.cla()


def plot_gain_amp(gain_sol, num_chunks, prefix="test"):
    """
    Plot gain amplitude for each antenna

    :param gain_sol: Gain solutions in shape (nants, nchan)
    :param num_chunks: Number of frequency chunks
    :param prefix: Unique plot name prefix (e.g. Meerkat)
    """
    plt.figure(figsize=(12, 6))
    nants = gain_sol.shape[0]
    solutions = gain_sol.reshape(
        (nants, num_chunks, gain_sol.shape[1] // num_chunks)
    )

    for chunk in range(num_chunks):
        to_plot = numpy.abs(solutions[:, chunk, :])
        plt.scatter(to_plot[0], to_plot[1], c="r")

    plt.ylabel("Number of antennas")
    plt.xlabel("Un-normalised G amplitude")

    plt.savefig(prefix + "_gain_amplitude.png")
    plt.cla()


def plot_vis_amp(vis, prefix="test"):
    """
    Plot Visibility amplitude data over time and frequency

    :param vis: A Visibility object
    :param prefix: Unique plot name prefix (e.g. Meerkat)
    """

    _, [ax1, ax2] = plt.subplots(1, 2, sharey=True)

    times = vis.time.data
    freqs = vis.frequency.data / 1.0e6
    vis_array = numpy.abs(vis.vis.data)

    # Visibility data is in (ntime, nbaselines, nchan, npol)
    # So we do averaging
    vis_array = numpy.mean(vis_array, axis=(1, 3))
    vis_per_time = numpy.mean(vis_array, axis=0)
    vis_per_freq = numpy.mean(vis_array, axis=1)

    ax1.plot(times, vis_per_time)
    ax2.plot(freqs, vis_per_freq)

    ax1.set_ylabel("Visibility amplitude")
    ax1.set_xlabel("Time [s]")
    ax2.set_xlabel("Frequency [MHz]")

    plt.title("Average visibility")
    plt.savefig(prefix + "_vis_amplitude.png")
    plt.cla()


# pylint:disable=too-many-locals
def plot_fitting(result, target, gain_sol, num_chunks, prefix="test"):
    """
    Plot fitting results in individual bands.
    Currently, for subplot design purposes
    we only support num_chunks=2**n.

    :param result: SolveForOffsets object
    :param target: Katpoint target object
    :param gain_sol: Gain solutions in shape (nants, nchan)
    :param num_chunks: Number of frequency bands
    :param prefix: Unique plot name prefix (e.g. Meerkat)
    """

    assert isinstance(
        numpy.sqrt(num_chunks), int
    ), "Number of chunks not supported"

    def _gauss_func(xparam, a_fac, mu_fac, sigma):
        return a_fac * numpy.exp(-((xparam - mu_fac) ** 2) / (2 * sigma**2))

    sample_x = numpy.arange(-1.2, 1.2, 0.1)

    try:
        # Check-- is this the right way to call them?
        beams = result.beams
        ants = result.ants
        freqs = result.freqs
        solutions = gain_sol.reshape(
            (len(ants), num_chunks, len(freqs) // num_chunks)
        )
        for i, antenna in enumerate(ants):
            fig, axis = plt.subplots(
                nrows=int(numpy.sqrt(num_chunks)),
                ncols=int(numpy.sqrt(num_chunks)),
                figsize=(18, 10),
            )
            fig.suptitle(
                f"Dish: {antenna.name} - Pointing fitting results", fontsize=24
            )
            axes = axis.flatten()

            relative_pos = numpy.c_[
                numpy.mean(target.azel[0], axis=0),
                numpy.mean(target.azel[1], axis=0),
            ]
            for chunk in range(num_chunks):
                x_param = relative_pos
                y_param = solutions[i, chunk, :]

                fit_c = beams[i].centre
                fit_w = beams[i].width
                fitted_h = beams[i].height

                axes[chunk].scatter(x_param[1][0:4], y_param[4:8])
                axes[chunk].scatter(x_param[1][0:4], y_param[0:4])
                axes[chunk].plot(
                    sample_x,
                    _gauss_func(
                        sample_x, fitted_h, fit_c[0], fit_w[0] / 2.35482
                    ),
                )
                axes[chunk].plot(
                    sample_x,
                    _gauss_func(
                        sample_x, fitted_h, fit_c[1], fit_w[1] / 2.35482
                    ),
                )
                axes[chunk].set_title(
                    f"freq = {int(freqs[chunk] / 1e6)} MHz", fontsize=12
                )

            plt.tight_layout()
            plt.savefig(prefix + "_fitting_results.png")
            plt.cla()

    except KeyError:
        log.error("Invalid SolveforOffsets object provided.")
