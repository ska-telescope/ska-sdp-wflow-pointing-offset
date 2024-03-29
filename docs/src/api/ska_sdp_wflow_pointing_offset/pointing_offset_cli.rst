ska\_sdp\_wflow\_pointing\_offset.pointing\_offset\_cli module
===============================================================

The command line interface to the pipeline for estimating the elevation and cross-elevation offsets
from a measurement set.

Usage
-----

.. code-block:: none

    > pointing_offset --help

    Program with many options using docopt for computing pointing offsets.

    Usage:
         pointing-offset COMMAND [--msdir=DIR] [--save_offset]
                          [--apply_mask] [--use_weights]
                          [--fit_to_vis] [--rfi_file=FILE]
                          [--results_dir=None] [--start_freq=None]
                          [--end_freq=None]
                          [(--bw_factor <bw_factor>) [<bw_factor>...]]
                          [--thresh_width=<float>][--time_avg=None]

    Commands:
        compute   Runs all required routines for computing the
        pointing offsets.

    Options:
      -h --help            show this help message and exit
      -q --quiet           report only file names

      --msdir=DIR           Directory including Measurement set files
      --fit_to_vis          Fit primary beam to visibilities instead of antenna
                            gains (Optional) [default:False]
      --apply_mask          Apply mask (Optional) [default:False]
      --use_weights         Use gain calibration weights when fitting for the
                            pointing offsets (Optional) [default:False]
      --rfi_file=FILE       RFI file (Optional)
      --save_offset         Save the offset results (Optional) [default:False]
      --results_dir=None    Directory where the results need to be saved (Optional)
      --start_freq=None     Start frequency in MHz (Optional)
      --end_freq=None       End frequency in MHz (Optional)
      --bw_factor           Beamwidth factor [default:0.976, 1.098]
      --thresh_width=<float>  The maximum ratio of the fitted to expected beamwidth
                              [default:1.5]
      --time_avg=None       Perform no, median, or mean time-averaging of the
                            gain amplitudes when fitting to gains. These options
                            can be set with None, "median", or "mean".


Commands \& Options
---------------------------
List of commands for accessing the functionalities of the pipeline.

.. list-table::
   :widths: 25 25
   :header-rows: 1

   * -
     - Action
   * - **compute**
     - Implements the list of actions below
   * - **msdir**
     - Directory containing measurement set for each discrete pointing scan
   * - **fit_to_vis**
     - Fit primary beam to visibilities instead of antenna gains
   * - **apply_mask**
     - Boolean to apply the RFI mask provided by the **rfi_file** command
   * - **use_weights**
     - Use weights when fitting primary beams to the gain amplitudes
   * - **rfi_file**
     - Filename containing RFI mask to be applied with the **apply_mask** command, in the format of .txt file
   * - **save_offset**
     - Boolean to save the fitted parameters and calculated offsets
   * - **results_dir**
     - Directory to save the fitted parameters and calculated offsets from the **save_offset** command
   * - **start_freq**
     - Start frequency in MHz to use
   * - **end_freq**
     - End frequency in MHz to use
   * - **bw_factor**
     - Beamwidth factors for the horizontal and vertical polarisations
   * - **thresh_width**
     - The maximum ratio of the fitted to expected beamwidth
   * - **time_avg**
     - Perform no, median, or mean time-averaging of the gain amplitudes when fitting to gains.
       These options can be set with None, ``median``, or ``mean``.
