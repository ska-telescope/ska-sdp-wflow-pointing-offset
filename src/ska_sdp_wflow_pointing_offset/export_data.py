# pylint: disable=invalid-name, duplicate-code， too-many-locals

"""
Functions of exporting data to csv file
"""

import numpy
import pandas

def export_pointing_offset_data(filename, offset):
    """
    Export results to a csv file.

    :param filename: file name
    :param offset: poiting offset
    :return: Boolean True-Success, False-Failed
    """

    assert isinstance(offset, numpy.ndarray)

    # convert array into dataframe
    data_frame = pandas.DataFrame(offset)

    # save the dataframe as a csv file
    data_frame.to_csv(filename)