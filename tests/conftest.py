""" Pytest fixtures """
import numpy
import pytest
from ska_sdp_datamodels.configuration.config_model import Configuration
from ska_sdp_datamodels.science_data_model.polarisation_model import (
    ReceptorFrame,
)
from ska_sdp_datamodels.visibility.vis_model import Visibility

from ska_sdp_wflow_pointing_offset import construct_antennas
from tests.utils import (
    ACTUAL_POINTING_EL,
    BASELINES,
    CHANNEL_BANDWIDTH,
    DIAMETER,
    FLAGS,
    FREQS,
    INTEGRATION_TIME,
    LOCATION,
    MOUNT,
    NAME,
    OFFSET,
    PHASECENTRE,
    POLARISATION_FRAME,
    SOURCE,
    SOURCE_OFFSET_AZ,
    SOURCE_OFFSET_EL,
    STATION,
    UVW,
    VIS,
    VIS_TIMESTAMPS,
    VIS_WEIGHTS,
    X_PER_SCAN,
    XYZ,
    Y_PER_SCAN_GAINS,
)

NANTS = 3


@pytest.fixture(name="configuration")
def configuration_fixture():
    """Configuration fixture"""
    return Configuration.constructor(
        name="SKAMID",
        location=LOCATION,
        names=numpy.array(NAME),
        xyz=XYZ,
        mount=MOUNT,
        frame="ITRF",
        receptor_frame=ReceptorFrame("linear"),
        diameter=DIAMETER,
        offset=OFFSET,
        stations=numpy.array(STATION),
    )


@pytest.fixture(name="ants")
def ants_fixture():
    """Antennas fixture"""
    return construct_antennas(XYZ, DIAMETER, STATION)


@pytest.fixture(name="source_offset")
def source_offset_fixture():
    """Source offset fixture"""
    return numpy.dstack((SOURCE_OFFSET_AZ, SOURCE_OFFSET_EL))


@pytest.fixture(name="vis_array")
def vis_array_fixture(configuration):
    """Visibility fixture"""
    return Visibility.constructor(
        frequency=FREQS,
        channel_bandwidth=CHANNEL_BANDWIDTH,
        phasecentre=PHASECENTRE,
        configuration=configuration,
        uvw=UVW,
        time=VIS_TIMESTAMPS,
        vis=VIS,
        weight=VIS_WEIGHTS,
        integration_time=INTEGRATION_TIME,
        flags=FLAGS,
        baselines=BASELINES,
        polarisation_frame=POLARISATION_FRAME,
        source=SOURCE,
        meta={"MSV2": {"FIELD_ID": 0, "DATA_DESC_ID": 0}},
    )


@pytest.fixture(name="frequency")
def freqs_fixture():
    """The frequencies of observation fixture"""
    return FREQS


@pytest.fixture(name="x_per_scan")
def x_per_scan_fixture():
    """The antenna positions per scan fixture"""
    return X_PER_SCAN


@pytest.fixture(name="y_per_scan_vis")
def y_per_scan_vis_fixture():
    """The visibility amplitudes of all antennas for each scan fixture"""
    return Y_PER_SCAN_VIS


@pytest.fixture(name="y_per_scan_gains")
def y_per_scan_gains_fixture():
    """The gain amplitudes of all antennas for each scan fixture"""
    return Y_PER_SCAN_GAINS
