ska\_sdp\_wflow\_pointing\_offset.pointing\_offset\_cli module
===============================================================

The command line interface to the pipeline for estimating the azimuth and elevation offsets from a
measurement set.

Usage
-----

.. code-block:: none

    > pointing_offset --help

    Program with many options using docopt for computing pointing offsets.

    Usage:
        pointing-offset COMMAND [--ms=FILE] [--save_offset]
                          [--apply_mask] [--fit_tovis]
                          [--rfi_file=FILE] [--results_dir=None]
                          [--start_freq=None] [--end_freq=None]
                          [(--bw_factor <bw_factor>) [<bw_factor>...]]

    Commands:
        compute   Runs all required routines for computing the
        pointing offsets.

    Options:
        -h --help            show this help message and exit
        -q --quiet           report only file names

        --ms=FILE            Measurement set file
        --fit_tovis          Fit primary beam to visibilities instead of antenna
                             gains (Optional) [default:False]
        --apply_mask         Apply Mask (Optional) [default:False]
        --rfi_file=FILE      RFI file (Optional)
        --save_offset        Save the Offset Results (Optional) [default:False]
        --results_dir=None   Directory where the results need to be saved (Optional)
        --start_freq=None    Start Frequency in MHz (Optional)
        --end_freq=None      End Frequency in MHz (Optional)
        --bw_factor          Beamwidth factor [default:0.976, 1.098]


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
   * - **ms**
     - Measurement set name
   * - **fit_tovis**
     - Fit primary beam to visibilities instead of antenna gains
   * - **apply_mask**
     - Boolean to apply the RFI mask provided by the **rfi_file** command
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


