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
    :return: True-Success, False-Failed
    """

    # convert array into dataframe
    data_frame = pandas.DataFrame(offset)

    # save the dataframe as a csv file
    data_frame.to_csv(filename)
