# pylint: disable=inconsistent-return-statements, too-few-public-methods
"""
Unit Tests to create GainTable
from CASA Tables
"""
import os
import tempfile

import numpy

from ska_sdp_wflow_pointing_offset.export_data import (
    export_pointing_offset_data,
)


def test_export_pointing_data_file():
    """
    Test importing gaintable from cal table
    """
    offset = numpy.array([[148.95, 35.62], [999.99, 99.99]])
    with tempfile.TemporaryDirectory() as temp_dir:

        filename = f"{temp_dir}/test_offset.csv"
        export_pointing_offset_data(filename, offset)
        assert os.path.exists(filename)
