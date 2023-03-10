ska\_sdp\_wflow\_pointing\_offset.pointing\_offset\_cli module
===============================================================

The command line interface to the pipeline for estimating the azimuth and elevation offsets from a
measurement set and metadata.

Usage
-----

.. code-block:: none

    > pointing_offset --help

    Program with many options using docopt for computing pointing offsets.

    Usage:
        pointing-offset COMMAND [--ms=FILE] [--rdb=FILE] [--save_offset]
                                [--apply_mask] [--rfi_file=FILE]
                                [--results_dir=None] [--start_freq=None]
                                [--end_freq=None] [--auto]

    Commands:
        compute   Runs all required routines for computing the
        pointing offsets.

    Options:
        -h --help            show this help message and exit
        -q --quiet           report only file names

        --rdb=FILE           RDB file
        --ms=FILE            Measurement set file
        --apply_mask         Apply Mask (Optional) [default:False]
        --rfi_file=FILE      RFI file (Optional)
        --save_offset        Save the Offset Results (Optional) [default:False]
        --results_dir=None   Directory where the results needs to be saved (Optional)
        --start_freq=None    Start Frequency (Optional)
        --end_freq=None      End Frequency (Optional)
        --auto               Auto-correlation visibilities (Optional) [default:False]


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
   * - **rdb**
     - Metadata name. Only rdb format is accepted
   * - **ms**
     - Measurement set name
   * - **apply_mask**
     - Boolean to apply the RFI mask provided by the **rfi_file** command
   * - **rfi_file**
     - Filename containing RFI mask to be applied with the **apply_mask** command. Only pickle format are read
   * - **save_offset**
     - Boolean to save the fitted parameters and calculated offsets
   * - **results_dir**
     - Directory to save the fitted parameters and calculated offsets from the **save_offset** command
   * - **start_freq**
     - Start frequency in Hz to use
   * - **end_freq**
     - End frequency in Hz to use
   * - **auto**
     - Boolean to read auto-correlation data or cross-correlation data

