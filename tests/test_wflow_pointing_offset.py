# pylint: disable=inconsistent-return-statements,too-many-arguments
""" Regression test for the pointing offset pipeline

"""
import logging
import os
import tempfile
from unittest.mock import patch

import numpy
import pytest

from ska_sdp_wflow_pointing_offset.pointing_offset_cli import compute_offset
from tests.utils import ANTS, DISH_COORD_AZ, DISH_COORD_EL, VIS_ARRAY

log = logging.getLogger("pointing-offset-logger")
log.setLevel(logging.WARNING)

DEFAULT_RUN = True
PERSIST = False


@patch("ska_sdp_wflow_pointing_offset.pointing_offset_cli.read_visibilities")
@pytest.mark.parametrize("fitting_method", [True, False])
@pytest.mark.parametrize(
    "enabled, mode, start_freq, end_freq",
    [
        (
            DEFAULT_RUN,
            "no_frequency_selection",
            None,
            None,
        ),
        (
            DEFAULT_RUN,
            "frequency_selection",
            8.562e8,
            8.567e8,
        ),
    ],
)
def test_wflow_pointing_offset(
    read_visibilities,
    fitting_method,
    enabled,
    mode,
    start_freq,
    end_freq,
):
    """
    Main test routine.
    Note: Mock ms.
          Currently, we don't test cases with RFI mask applied,
          Please refer to the unit tests for apply_rfi_mask.

    :param enabled: Is this test enabled?
    :param mode: Which mode it is testing
    :param start_freq: Start frequency (Hz)
    :param end_freq: End frequency (Hz)
    """

    if not enabled:
        log.warning(
            "test_pointing_offset: test of %s mode is disabled, "
            "use enabled argument to change.",
            mode,
        )
        return True

    with tempfile.TemporaryDirectory() as tempdir:
        log.info("Putting output data into temporary %s.", tempdir)

        outfile = f"{tempdir}/pointing_offsets.txt"
        beamwidth_factor = [0.976, 1.098]

        read_visibilities.return_value = (
            VIS_ARRAY,
            numpy.dstack((DISH_COORD_AZ, DISH_COORD_EL)),
            ANTS,
        )

        args = {
            "--start_freq": start_freq,
            "--end_freq": end_freq,
            "--apply_mask": False,
            "--rfi_file": None,
            "--save_offset": True,
            "--fit_to_vis": fitting_method,
            "--results_dir": tempdir,
            "--ms": tempdir,
            "--bw_factor": True,
            "<bw_factor>": beamwidth_factor,
        }

        compute_offset(args)

        assert os.path.exists(outfile)

        read_out = numpy.loadtxt(outfile, delimiter=",")
        # Output data shape [nants, 20]
        assert read_out.shape == (3, 20)

        # If we need to save file to tests directory
        if PERSIST:
            log.info("Putting data into test_results directory.")
            test_dir = os.getcwd() + "/test_results"
            os.makedirs(test_dir, exist_ok=True)
            new_name = test_dir + "/pointing_offsets_" + f"{mode}" + ".txt"
            os.replace(outfile, new_name)
