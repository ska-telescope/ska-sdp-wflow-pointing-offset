Docker image
============

A Docker image is also available and it has all the requirements installed.

It is available from the
`Central Artifact Repository <https://artefact.skao.int/#browse/browse:docker-all>`_::

    artefact.skao.int/ska-sdp-wflow-pointing-offset

Please refer to the repository for the latest version.

The image is based on `python:3.10-slim` and its entrypoint is ["pointing-offset"].
Running the Docker image will be just like running a command line application.

In order to run the pipeline using the compute option, execute the following::

    docker run -it -v ${PWD}:/data artefact.skao.int/ska-sdp-wflow-pointing-offset:0.1.0 compute --ms=/data/test.ms

Make sure you run this from the directory where the Measurement Set is (test.ms in this case),
and use the right tag.
The other command line arguments follows as the example above.