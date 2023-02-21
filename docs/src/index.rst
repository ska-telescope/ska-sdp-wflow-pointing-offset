SKA SDP Pointing Offset Calibration Pipeline
============================================
This is a `repository`_ for the SDP pointing offset calibration pipeline. This repository provides sets of Python functions for reading
measurement set and metadata (currently supports only RDB file format for the MeerKAT array) necessary for computing the azimuth and
elevation offsets for local pointing correction. The offsets are computed by fitting the primary beam (modelled by a 2D Gaussian) to
the auto-correlation or cross-correlation visibility amplitudes of each antenna. Note that the final pipeline would instead fit primary beams to the complex
gains of each antenna (derived possibly from the gain solver in `RASCIL`_). These set of functions used in this pipeline are based on
those used by the `SARAO`_ team for computing pointing offsets for the MeerKAT array.

.. image:: images/functionality_diagram.png
  :width: 500%
  :alt: Pointing Offset Functionality Diagram

Installation Instructions
============================================
The package is installable via pip.

If you would like to view the source code or install from git, use::

  git clone https://gitlab.com/ska-telescope/sdp/science-pipeline-workflows/ska-sdp-wflow-pointing-offset.git
    
Please ensure you have all the dependency packages installed. The installation is managed through `poetry`_. Refer to their page for
instructions.

.. toctree::
   :maxdepth: 1

   api/index


.. toctree::
   :maxdepth: 1
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _repository: https://gitlab.com/ska-telescope/sdp/science-pipeline-workflows/ska-sdp-wflow-pointing-offset
.. _poetry: https://python-poetry.org/docs/
.. _SARAO: https://www.sarao.ac.za/
.. _RASCIL: https://gitlab.com/ska-telescope/external/rascil-main
