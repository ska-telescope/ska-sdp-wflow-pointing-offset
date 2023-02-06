"""
Util functions for plotting
"""
import matplotlib.pyplot as plt


def plot_azel(az_data, el_data):
    """
    Plot az, el for visual examination.
    """

    plt.figure(figsize=(10, 5))
    plt.plot(az_data, el_data, "bo", label="Approach 1")
    plt.xlabel("Azimuth [degrees]")
    plt.ylabel("Elevation [degrees]")
    plt.title("Converting (x,y) -> (az, el)")
    plt.savefig("az_el_plot.png")
