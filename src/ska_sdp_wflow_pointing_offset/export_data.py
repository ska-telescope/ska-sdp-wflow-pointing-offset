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
        for each polaristion. The columns of the data are : Fitted
        beam centre and uncertainty, fitted beamwidth and uncertainty,
        fitted beam height and uncertainty
    :return: True-Success, False-Failed
    """

    numpy.savetxt(filename, offset, delimiter=",")
