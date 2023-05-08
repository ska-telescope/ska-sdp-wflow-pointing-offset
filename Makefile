include .make/base.mk
include .make/python.mk
include .make/oci.mk


PROJECT_NAME = ska-sdp-wflow-pointing-offset

# E203: whitespace before ':'
# W503: line break before binary operator
PYTHON_SWITCHES_FOR_FLAKE8 = --ignore=E203,W503

