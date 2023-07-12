"""
Functions for exporting pointing offset data to text file
"""

import numpy


def export_pointing_offset_data(filename, offset):
    """
    Writes the results of the pointing offset calibration
    results to a text file.

    :param filename: file name
    :param offset: The fitted azimuth and elevation offsets
        and cross-elevation offset for each antenna
    :return: True-Success, False-Failed
    """

    header = (
        "Antenna Name Azimuth Offset Elevation Offset Cross-elevation Offset"
    )
    numpy.savetxt(filename, offset, fmt="%s", header=header, delimiter=",")
