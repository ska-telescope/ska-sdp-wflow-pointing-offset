# pylint: disable=inconsistent-return-statements, too-few-public-methods
"""
Unit Tests to create GainTable
from CASA Tables
"""
from unittest.mock import patch

import numpy
import pytest
import os

from ska_sdp_wflow_pointing_offset.export_data import (
    export_pointing_offset_data
)

def test_export_pointing_data_file():
    """
    Test importing gaintable from cal table
    """
    offset = numpy.array([[148.95,35.62],[999.99,99.99]])
    export_pointing_offset_data("test_offset.csv",offset)

    assert os.path.exists("test_offset.csv") == True
    os.remove("test_offset.csv")
