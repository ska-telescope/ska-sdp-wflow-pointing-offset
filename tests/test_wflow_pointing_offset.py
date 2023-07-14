# pylint: disable=inconsistent-return-statements,too-many-arguments
# pylint: disable=too-many-locals
""" Regression test for the pointing offset pipeline

"""
import logging
import os
import tempfile
from unittest.mock import patch

import numpy
import pytest

from ska_sdp_wflow_pointing_offset.pointing_offset_cli import compute_offset

log = logging.getLogger("pointing-offset-logger")
log.setLevel(logging.WARNING)

DEFAULT_RUN = True
PERSIST = False


@patch(
    "ska_sdp_wflow_pointing_offset.pointing_offset_cli.read_batch_visibilities"
)
@pytest.mark.parametrize("fitting_method", [True, False])
@pytest.mark.parametrize("use_weights", [True, False])
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
    read_batch_visibilities,
    fitting_method,
    use_weights,
    enabled,
    mode,
    start_freq,
    end_freq,
    vis_array,
    source_offset,
    offset_timestamps,
    ants,
    target,
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
        thresh_width = 1.5
        num_chunks = 1

        read_batch_visibilities.return_value = (
            vis_array,
            source_offset,
            offset_timestamps,
            ants,
            target,
        )

        args = {
            "--start_freq": start_freq,
            "--end_freq": end_freq,
            "--apply_mask": False,
            "--rfi_file": None,
            "--save_offset": True,
            "--fit_to_vis": fitting_method,
            "--use_weights": use_weights,
            "--results_dir": tempdir,
            "--msdir": tempdir,
            "--bw_factor": True,
            "<bw_factor>": beamwidth_factor,
            "--thresh_width": thresh_width,
            "--time_avg": None,
            "--num_chunks": num_chunks,
        }

        compute_offset(args)

        assert os.path.exists(outfile)

        read_out = numpy.loadtxt(outfile, delimiter=",", dtype=object)

        # Output data: Antenna name, Az offset, El offset, Cross-el offset
        # The Az and El offsets are asserted in test_beam_fitting.py
        # After ORC-1716, only teh shape would be required all of these
        # assertions would be done in test_beam_fitting.py
        assert read_out.shape == (3, 4)
        assert (read_out[:, 0] == ["M001", "M002", "M003"]).all()

        if use_weights:
            if fitting_method:
                assert (numpy.isnan(read_out[:, 1].astype(float)[0])).all()
                assert (
                    read_out[:, 1].astype(float)[1:] == numpy.zeros(2)
                ).all()

                assert (numpy.isnan(read_out[:, 2].astype(float)[0])).all()
                assert (
                    read_out[:, 2].astype(float)[1:]
                    == numpy.array([-10.597531820892497, 11.014530406730886])
                ).all()
                assert (numpy.isnan(read_out[:, 3].astype(float)[0])).all()
                assert (
                    read_out[:, 3].astype(float)[1:] == numpy.array([0.0, 0.0])
                ).all()
            else:
                assert (
                    read_out[:, 1].astype(float)[0]
                    == numpy.array([0.0, 0.0, 0.0])
                ).all()
        else:
            if fitting_method:
                assert (numpy.isnan(read_out[:, 1].astype(float)[0])).all()
                assert (
                    read_out[:, 1].astype(float)[1:] == numpy.zeros(2)
                ).all()

                assert (numpy.isnan(read_out[:, 2].astype(float)[0])).all()
                assert (
                    read_out[:, 2].astype(float)[1:]
                    == numpy.array([-10.597531820892497, 11.014530406730886])
                ).all()
                assert (numpy.isnan(read_out[:, 3].astype(float)[0])).all()
                assert (
                    read_out[:, 3].astype(float)[1:] == numpy.array([0.0, 0.0])
                ).all()
            else:
                assert (numpy.isnan(read_out[:, 1].astype(float))).all()
                assert (numpy.isnan(read_out[:, 2].astype(float))).all()
                assert (numpy.isnan(read_out[:, 3].astype(float))).all()

        # If we need to save file to tests directory
        if PERSIST:
            log.info("Putting data into test_results directory.")
            test_dir = os.getcwd() + "/test_results"
            os.makedirs(test_dir, exist_ok=True)
            new_name = test_dir + "/pointing_offsets_" + f"{mode}" + ".txt"
            os.replace(outfile, new_name)
