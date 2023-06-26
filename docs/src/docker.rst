Docker image
============

A Docker image is also available, which contains the full
contents of the repository, and it has all the requirements installed.

It is available from the
`Central Artifact Repository <https://artefact.skao.int/#browse/browse:docker-all>`_::

    artefact.skao.int/ska-sdp-wflow-pointing-offset

Please refer to the repository for the latest version, currently it is at 0.0.0.

The image is based on `python:3.10-slim` and its entrypoint is ["pointing-offset"].
Running the Docker image will start a python:3.10 shell.

In order to run the pipeline using the compute option, execute the following::

    docker run -it -v ${PWD}:/data artefact.skao.int/ska-sdp-wflow-pointing-offset:0.0.0 compute --ms=/data/test.ms

Make sure you run this from the directory where the Measurement Set is (test.ms in this case).
The other command line arguments follows as the example above.