"""
Functions of exporting data to csv file
"""

import numpy


def export_pointing_offset_data(filename, offset):
    """
    Export results to a csv file.

    :param filename: file name
    :param offset: Fitted parameters and pointing offsets.
    # The columns of the data are : Antenna Name, Fitting
    flag, fitted beam centre and uncertainty, fitted beamwith
    and uncertainty, fitted beam height and uncertainty,
    fitted beam centre (in azel), commanded (azel), delta Az,
    delta El
    :return: True-Success, False-Failed
    """

    numpy.savetxt(filename, offset, delimiter=",")
