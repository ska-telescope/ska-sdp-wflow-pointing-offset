Docker image
============

A Docker image is also available, which contains the full
contents of the repository, and it has all the requirements installed.

It is available from the
`Central Artifact Repository <https://artefact.skao.int/#browse/browse:docker-all>`_::

    artefact.skao.int/ska-sdp-wflow-pointing-offset

Please refer to the repository for the latest version, and other available versions.
The first version we published is 0.0.0.

The image is based on `python:3.10-slim` and its entrypoint is ["pointing-offset"].
Running the Docker image will start a python:3.10 shell.

In order to run the pipeline using the compute option, execute the following::

    docker run -it artefact.skao.int/ska-sdp-wflow-pointing-offset:0.1.0 compute --ms=test.ms

The other command line arguments follows as the example above. Make sure you use the correct tag.
