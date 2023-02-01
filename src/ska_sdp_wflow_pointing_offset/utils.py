"""
Util functions for plotting
"""

import matplotlib.pyplot as plt


def plot_azel(az, el):
    """
    Plot az, el in degrees
    :param az:
    :param el:
    :return:
    """

    plt.figure(figsize=(10, 5))
    plt.plot(az, el, "bo")
    plt.xlabel("Azimuth [degrees]")
    plt.ylabel("Elevation [degrees]")
    plt.title("Pointing offset information")
    plt.savefig("azel.png")
