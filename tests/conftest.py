""" Pytest fixtures """
import numpy
import pytest
from ska_sdp_datamodels.calibration.calibration_model import GainTable
from ska_sdp_datamodels.configuration.config_model import Configuration
from ska_sdp_datamodels.science_data_model.polarisation_model import (
    ReceptorFrame,
)
from ska_sdp_datamodels.visibility.vis_model import Visibility

from ska_sdp_wflow_pointing_offset import construct_antennas
from tests.utils import (
    BASELINES,
    CHANNEL_BANDWIDTH,
    DIAMETER,
    DISH_COORD_AZ,
    DISH_COORD_EL,
    FLAGS,
    FREQS,
    GAIN,
    GAIN_RESIDUAL,
    GAIN_WEIGHT,
    INTEGRATION_TIME,
    INTERVAL,
    LOCATION,
    MOUNT,
    NAME,
    OFFSET,
    PHASECENTRE,
    POLARISATION_FRAME,
    SOURCE,
    STATION,
    TIMESTAMPS,
    UVW,
    VIS,
    VIS_WEIGHTS,
    XYZ,
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
    return numpy.dstack((DISH_COORD_AZ, DISH_COORD_EL))


@pytest.fixture(name="vis_array")
def vis_array_fixture(configuration):
    """Visibility fixture"""
    return Visibility.constructor(
        frequency=FREQS,
        channel_bandwidth=CHANNEL_BANDWIDTH,
        phasecentre=PHASECENTRE,
        configuration=configuration,
        uvw=UVW,
        time=TIMESTAMPS,
        vis=VIS,
        weight=VIS_WEIGHTS,
        integration_time=INTEGRATION_TIME,
        flags=FLAGS,
        baselines=BASELINES,
        polarisation_frame=POLARISATION_FRAME,
        source=SOURCE,
        meta={"MSV2": {"FIELD_ID": 0, "DATA_DESC_ID": 0}},
    )


@pytest.fixture(name="gain_array")
def gain_array_fixture(configuration):
    """Antenna gains fixture"""
    return GainTable.constructor(
        gain=GAIN,
        time=TIMESTAMPS,
        interval=INTERVAL,
        weight=GAIN_WEIGHT,
        residual=GAIN_RESIDUAL,
        frequency=numpy.ravel(numpy.mean(FREQS)),
        receptor_frame=ReceptorFrame("linear"),
        phasecentre=PHASECENTRE,
        configuration=configuration,
        jones_type="G",
    )
