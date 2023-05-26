"""
Functions for exporting pointing offset data to text file
"""

import numpy


def export_pointing_offset_data(filename, offset):
    """
    Writes the results of the pointing offset calibration
    results to a text file.

    :param filename: file name
    :param offset: The fitted parameters and their uncertainties
        for each polaristion. The columns of the data are : AzEl
        offset and their uncertainties, cross-elevation offset and
        its uncertainty, fitted beamwidth and its uncertainty,
        fitted beam height and its uncertainty
    :return: True-Success, False-Failed
    """

    numpy.savetxt(filename, offset, delimiter=",")
