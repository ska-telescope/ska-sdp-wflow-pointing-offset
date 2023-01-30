# pylint: disable=inconsistent-return-statements, too-few-public-methods
"""
Unit Tests to create GainTable
from CASA Tables
"""
from unittest.mock import patch

import numpy
import pytest

from ska_sdp_wflow_pointing_offset.read_data import (
    read_cross_correlation_visibilities,
)

NTIMES = 4
NANTS = 6
NFREQ = 3
TEL_NAME = "MY-SKA"


class MockBaseTable:
    """
    Mock Base Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "TIME":
            return numpy.array(
                [4.35089331e09, 4.35089332e09, 4.35089333e09, 4.35089334e09]
            )

        if columnname == "INTERVAL":
            return numpy.array([10.0])

        if columnname == "CPARAM":
            return numpy.ones((NTIMES, NANTS, NFREQ, 1))

        if columnname == "ANTENNA1":
            return numpy.array([0, 1, 2, 3, 4, 5])

        if columnname == "SPECTRAL_WINDOW_ID":
            return numpy.array([0, 1])


class MockSpectralWindowTable:
    """
    Mock Spectral Window Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "CHAN_FREQ":
            return numpy.array([[8.0e9, 8.1e9, 8.2e9], [8.4e9, 8.5e9, 8.6e9]])

        if columnname == "NUM_CHAN":
            return numpy.array([NFREQ, NFREQ])


class MockAntennaTable:
    """
    Mock Antenna Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name from MS File
        """
        if columnname == "NAME":
            return ["ANT1", "ANT2", "ANT3", "ANT4", "ANT5", "ANT6"]

        if columnname == "MOUNT":
            return ["ALT-AZ", "ALT-AZ", "ALT-AZ", "ALT-AZ", "ALT-AZ", "ALT-AZ"]

        if columnname == "DISH_DIAMETER":
            return numpy.array([25.0, 25.0, 25.0, 25.0, 25.0, 25.0])

        if columnname == "POSITION":
            return numpy.array(
                [
                    [-1601162.0, -5042003.0, 3554915.0],
                    [-1601192.0190292, -5042007.78341262, 3554960.73493029],
                    [-1601147.19047704, -5042040.12425644, 3554894.80919799],
                    [-1601110.11175873, -5041807.16312437, 3554839.91628013],
                    [-1601405.58491341, -5042041.04214758, 3555275.06577525],
                    [-1601093.35329757, -5042182.23690452, 3554815.49897078],
                ]
            )

        if columnname == "OFFSET":
            return numpy.array(
                [
                    [0.00000000e00, 0.00000000e00, 0.00000000e00],
                    [2.18848512e-03, 0.00000000e00, 0.00000000e00],
                    [-3.02790361e-03, 0.00000000e00, 0.00000000e00],
                    [-9.89315100e-04, 0.00000000e00, 0.00000000e00],
                    [5.09647129e-04, 0.00000000e00, 0.00000000e00],
                    [-2.87800725e-03, 0.00000000e00, 0.00000000e00],
                ]
            )

        if columnname == "STATION":
            return [
                "SKAMID-CORE",
                "SKAMID-CORE",
                "SKAMID-CORE",
                "SKAMID-ARM1",
                "SKAMID-ARM2",
                "SKAMID-ARM3",
            ]


class MockFieldTable:
    """
    Mock Field Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name from a table
        """
        if columnname == "PHASE_DIR":
            return numpy.array([[[0.0, 0.0]]])


class MockObservationTable:
    """
    Mock Observation Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "TELESCOPE_NAME":
            return TEL_NAME


casacore = pytest.importorskip("python-casacore")


@patch("ska_sdp_wflow_pointing_offset.read_data._load_ms_tables")
def test_read_cross_correlation_visibilities(mock_tables):
    """
    Test importing gaintable from cal table
    """
    mock_tables.return_value = (
        MockAntennaTable(),
        MockBaseTable(),
        MockFieldTable(),
        MockObservationTable(),
        MockSpectralWindowTable(),
    )
    vis, freqs = read_cross_correlation_visibilities("test_table")
    assert isinstance(vis, numpy.ndarray)
    assert isinstance(freqs, numpy.ndarray)

    # Specific attributes
    expected_time = numpy.array(
        [4.35089331e09, 4.35089332e09, 4.35089333e09, 4.35089334e09]
    )
    # assert (result.coords["time"] == expected_time).all()
    # assert (result.interval.data[...] == 10.0).all()
    # assert (result.gain.data[..., 0, 0] == complex(1.0, 0.0)).all()
    # assert (result.gain.data[..., 0, 1] == complex(0.0, 0.0)).all()
    # assert (result.weight.data[...] == 1.0).all()
    # assert (result.residual.data[...] == 0.0).all()
