"""
Functions of exporting data to csv file
"""

import numpy


def export_pointing_offset_data(filename, offset):
    """
    Export results to a csv file.

    :param filename: file name
    :param offset: poiting offset
    :return: True-Success, False-Failed
    """

    numpy.savetxt(filename, offset, delimiter=",")
