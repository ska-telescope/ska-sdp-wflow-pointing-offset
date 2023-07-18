"""
Unit test for plotting functions.
Currently test only asserts plotting is successful.
To further test, we need to assert number of plot calls.
"""
import os

import numpy

from ska_sdp_wflow_pointing_offset.plotting_func import (
    plot_fitting,
    plot_gain_amp,
    plot_offsets,
    plot_vis_amp,
)
from tests.utils import SOURCE_OFFSET_AZ, SOURCE_OFFSET_EL


def test_plot_offsets():
    """
    Test for plot_offsets
    """

    offset_azel = numpy.dstack((SOURCE_OFFSET_AZ, SOURCE_OFFSET_EL))
    plot_offsets(offset_azel[0], SOURCE_OFFSET_EL[0])

    assert os.path.exists("test_azel_offset.png")
    os.remove("test_azel_offset.png")


def test_plot_gain_amp():
    """
    Test for plot_gain_gamp
    """

    pass


def test_plot_vis_amp():
    """
    Test for plot_vis_gamp
    """

    pass


def test_plot_fitting():
    """
    Test for plot_fitting
    """

    pass
