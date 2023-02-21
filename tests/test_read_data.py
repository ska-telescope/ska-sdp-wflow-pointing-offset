# pylint: disable=inconsistent-return-statements,too-many-return-statements
# pylint: disable=too-few-public-methods
"""
Unit Tests to read data
from CASA Measurement Tables
"""
from unittest.mock import patch

import numpy
import pytest

from ska_sdp_wflow_pointing_offset.read_data import read_visibilities

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

        if columnname == "DATA":
            return numpy.array([1, 2, 3, 4, 5, 6, 7, 8, 9])

        if columnname == "WEIGHT":
            return numpy.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])


class MockSpectralWindowTable:
    """
    Mock Spectral Window Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "CHAN_FREQ":
            return numpy.array([8.0e9, 8.1e9, 8.2e9])

        if columnname == "NUM_CHAN":
            return numpy.array([NFREQ])


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


class MockPolarisationTable:
    """
    Mock Polarisation Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "CORR_TYPE":
            return numpy.array([9, 12])


class MockSourceTable:
    """
    Source Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "NAME":
            return ["J1939-6342"]
        if columnname == "DIRECTION":
            return numpy.array([[5.1461782, -1.11199581]])


casacore = pytest.importorskip("casacore")


@patch("ska_sdp_wflow_pointing_offset.read_data._load_ms_tables")
def test_read_visibilities(mock_tables):
    """
    Test importing gaintable from cal table
    """
    mock_tables.return_value = (
        MockAntennaTable(),
        MockBaseTable(),
        MockPolarisationTable(),
        MockSpectralWindowTable(),
        MockSourceTable(),
    )
    (
        vis,
        freqs,
        corr_type,
        vis_weight,
        target,
    ) = read_visibilities("test_table")
    assert isinstance(vis, numpy.ndarray)
    assert isinstance(freqs, numpy.ndarray)

    # Specific attributes
    assert (vis == numpy.array([1, 2, 3, 4, 5, 6, 7, 8, 9])).all()
    assert (freqs == numpy.array([8.0e9, 8.1e9, 8.2e9])).all()
    assert (corr_type == numpy.array(["XX", "YY"])).all()
    assert (
        vis_weight
        == numpy.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    ).all()
    assert target.radec() == (5.1461782, -1.11199581)