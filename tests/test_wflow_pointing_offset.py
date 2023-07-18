# pylint: disable=inconsistent-return-statements,too-many-arguments
# pylint: disable=too-many-locals,too-many-statements)
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
@pytest.mark.parametrize("num_chunks", [1, 16])
@pytest.mark.parametrize("fitting_type", [True, False])
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
    num_chunks,
    fitting_type,
    use_weights,
    enabled,
    mode,
    start_freq,
    end_freq,
    vis_array,
    source_offset,
    pointing_timestamps,
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
    :param vis_array: List of Visibility objects
    :param source_offset: Antenna positions relative to the
        pointing calibrator in azel coordinates
    :param pointing_timestamps: Source offset timestamps
    :param ants: List of katpoint antennas
    :param target: katpoint target
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
        thresh_width = 1.15

        read_batch_visibilities.return_value = (
            vis_array,
            source_offset,
            pointing_timestamps,
            ants,
            target,
        )

        args = {
            "--start_freq": start_freq,
            "--end_freq": end_freq,
            "--apply_mask": False,
            "--rfi_file": None,
            "--save_offset": True,
            "--num_chunks": num_chunks,
            "--fit_to_vis": fitting_type,
            "--use_weights": use_weights,
            "--results_dir": tempdir,
            "--msdir": tempdir,
            "--bw_factor": True,
            "<bw_factor>": beamwidth_factor,
            "--thresh_width": thresh_width,
            "--time_avg": None,
        }

        compute_offset(args)

        assert os.path.exists(outfile)

        read_out = numpy.loadtxt(outfile, delimiter=",", dtype=object)

        # Output data: Antenna name, Az offset, El offset, Cross-el offset
        # nan values for the offsets indicate no valid fits were obtained
        # and zero values indicate no offsets need to be applied to the
        # antenna pointings
        assert read_out.shape == (3, 4)
        assert (read_out[:, 0] == ["M001", "M002", "M003"]).all()
        if num_chunks > 1:
            # When fitting to gains only
            if not fitting_type:  # fitting to visibility
                if use_weights:
                    assert (
                        numpy.isnan(read_out[:, 1].astype(float)[:2])
                    ).all()
                    assert read_out[:, 1].astype(float)[2] == 0.0
                    assert (numpy.isnan(read_out[:, 2].astype(float))).all()
                    assert (
                        numpy.isnan(read_out[:, 2].astype(float)[:2])
                    ).all()
                    assert (
                        numpy.isnan(read_out[:, 3].astype(float)[:2])
                    ).all()
                    assert read_out[:, 3].astype(float)[2] == 0.0
                else:
                    assert read_out[:, 1].astype(float)[0] == 0.0
                    assert (numpy.isnan(read_out[:, 1].astype(float)[1])).all()
                    assert read_out[:, 1].astype(float)[2] == 0.0
                    numpy.testing.assert_almost_equal(
                        read_out[:, 2].astype(float)[:2],
                        numpy.array([-18.492012, -0.635930]),
                        decimal=6,
                    )
                    assert (numpy.isnan(read_out[:, 2].astype(float)[2])).all()
                    assert read_out[:, 3].astype(float)[0] == 0.0
                    assert (numpy.isnan(read_out[:, 3].astype(float)[1])).all()
                    assert read_out[:, 3].astype(float)[2] == 0.0
        else:
            # When fitting to visibility and gains
            if fitting_type:  # fitting to visibility
                if not use_weights:
                    # weights are not used when fitting to visibility
                    assert (numpy.isnan(read_out[:, 1].astype(float)[0])).all()
                    assert read_out[:, 1].astype(float)[1] == 0.0
                    assert read_out[:, 1].astype(float)[2] == 0.0

                    assert (numpy.isnan(read_out[:, 2].astype(float)[0])).all()
                    numpy.testing.assert_almost_equal(
                        read_out[:, 2].astype(float)[1:],
                        numpy.array([-15.626522, -21.253288]),
                        decimal=6,
                    )
                    assert (numpy.isnan(read_out[:, 3].astype(float)[0])).all()
                    assert (
                        read_out[:, 3].astype(float)[1:]
                        == numpy.array([0.0, 0.0])
                    ).all()
            else:  # fitting to gains
                if use_weights:
                    assert (
                        read_out[:, 1].astype(float)
                        == numpy.array([0.0, 0.0, 0.0])
                    ).all()
                    numpy.testing.assert_almost_equal(
                        read_out[:, 2].astype(float),
                        numpy.array([-23.450353, -1.803029, -2.010596]),
                        decimal=6,
                    )
                    assert (
                        read_out[:, 3].astype(float)
                        == numpy.array([0.0, 0.0, 0.0])
                    ).all()
                else:
                    assert (numpy.isnan(read_out[:, 1].astype(float)[0])).all()
                    assert (
                        read_out[:, 1].astype(float)[1:]
                        == numpy.array([0.0, 0.0])
                    ).all()
                    assert (numpy.isnan(read_out[:, 2].astype(float)[0])).all()
                    numpy.testing.assert_almost_equal(
                        read_out[:, 2].astype(float)[1:],
                        numpy.array([-19.701555, -1.958396]),
                        decimal=6,
                    )
                    assert (numpy.isnan(read_out[:, 3].astype(float)[0])).all()
                    assert (
                        read_out[:, 3].astype(float)[1:]
                        == numpy.array([0.0, 0.0])
                    ).all()

        # If we need to save file to tests directory
        if PERSIST:
            log.info("Putting data into test_results directory.")
            test_dir = os.getcwd() + "/test_results"
            os.makedirs(test_dir, exist_ok=True)
            new_name = test_dir + "/pointing_offsets_" + f"{mode}" + ".txt"
            os.replace(outfile, new_name)
