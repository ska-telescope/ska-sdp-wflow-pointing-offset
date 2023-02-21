ska\_sdp\_wflow\_pointing\_offset.pointing\_offset\_cli module
=====================================================
Command Line Interface: ``pointing_offset``

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


.. automodule:: ska_sdp_wflow_pointing_offset.pointing_offset_cli
   :members:
   :undoc-members:
   :show-inheritance:
