"""
Functions for plotting and visualisation of outputs
"""

import logging

import matplotlib.pyplot as plt
import numpy

log = logging.getLogger("ska-sdp-pointing-offset")


def plot_azel(offset_azel):
    """
    Scatter plot of azimuth and elevation offset.

    :param offset_azel: Offset array in arcseconds
    """
    plt.figure(figsize=(12, 6))

    plt.scatter(offset_azel[:, 0] * 60.0, offset_azel[:, 1] * 60.0, c="r")

    plt.ylabel("Elevation (arcminutes)")
    plt.xlabel("Azimuth offset (arcminutes)")

    plt.savefig("Azel_offset.png")
    plt.cla()


def plot_gain_amp(gain_sol, num_chunks):
    """
    Plot gain amplitude for each antenna

    :param gain_sol: Gain solutions in shape (nants, nchan)
    :param num_chunks: Number of frequency chunks
    """
    plt.figure(figsize=(12, 6))
    nants = gain_sol.shape[0]
    solutions = gain_sol.reshape(
        (nants, num_chunks, gain_sol.shape[1] // num_chunks)
    )

    for chunk in range(num_chunks):
        to_plot = solutions[:, chunk, :]
        plt.scatter(to_plot[0], to_plot[1], c="r")

    plt.ylabel("Number of antennas")
    plt.xlabel("Un-normalised G amplitude")

    plt.savefig("gain_amplitude.png")
    plt.cla()


def plot_fitting(result, targets, gain_sol, num_chunks):
    """
    Plot fitting results in individual bands.
    Currently, for subplot design purposes
    we only support num_chunks=2**n.

    :param result: SolveForOffsets object
    :param targets: Katpoint targets in (x, y)
    :param gain_sol: Gain solutions in shape (nants, nchan)
    :param num_chunks: Number of frequency bands
    """

    assert isinstance(
        numpy.sqrt(num_chunks), int
    ), "Number of chunks not supported"

    def _gauss_func(x, a, mu, sigma):
        return a * numpy.exp(-((x - mu) ** 2) / (2 * sigma**2))

    sample_x = numpy.arange(-1.2, 1.2, 0.1)

    try:
        beams = result.beams
        ants = result.ants
        freqs = result.freqs
        solutions = gain_sol.reshape(
            (len(ants), num_chunks, len(freqs) // num_chunks)
        )
        for i, antenna in enumerate(ants):
            fig, ax = plt.subplots(
                nrows=int(numpy.sqrt(num_chunks)),
                ncols=int(numpy.sqrt(num_chunks)),
                figsize=(18, 10),
            )
            fig.suptitle(
                f"Dish: {antenna.name} - Pointing fitting results", fontsize=24
            )
            ax = ax.flatten()

            relative_pos = numpy.c_[
                numpy.mean(targets[0], axis=0), numpy.mean(targets[1], axis=0)
            ]
            for chunk in range(num_chunks):
                x_param = relative_pos
                y_param = solutions[i, chunk, :]

                fit_c = beams[i].centre
                fit_w = beams[i].width
                fitted_h = beams[i].height

                ax[chunk].scatter(x_param[1][0:4], y_param[4:8])
                ax[chunk].scatter(x_param[1][0:4], y_param[0:4])
                ax[chunk].plot(
                    sample_x,
                    _gauss_func(
                        sample_x, fitted_h, fit_c[0], fit_w[0] / 2.35482
                    ),
                )
                ax[chunk].plot(
                    sample_x,
                    _gauss_func(
                        sample_x, fitted_h, fit_c[1], fit_w[1] / 2.35482
                    ),
                )
                ax[chunk].set_title(
                    f"freq = {int(freqs[chunk] / 1e6)} MHz", fontsize=12
                )

            plt.tight_layout()
            plt.save("fitting_results.png")
            plt.cla()

    except KeyError:
        log.error("Invalid SolveforOffsets object provided.")
