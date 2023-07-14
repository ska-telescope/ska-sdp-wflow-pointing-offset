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
    POINTING_TIMESTAMPS,
    POLARISATION_FRAME,
    SOURCE,
    SOURCE_OFFSET_AZ,
    SOURCE_OFFSET_EL,
    STATION,
    TARGET,
    UVW,
    VIS,
    VIS_TIMESTAMPS,
    VIS_WEIGHTS,
    WEIGHTS_PER_SCAN,
    X_PER_SCAN,
    XYZ,
    Y_PER_SCAN_GAINS,
    Y_PER_SCAN_VIS,
)

NANTS = 3
NSCANS = 5
NUM_CHUNKS = 16


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
    source_offset_list = []
    for _ in range(NSCANS):
        source_offset_list.append(
            numpy.dstack((SOURCE_OFFSET_AZ, SOURCE_OFFSET_EL))
        )
    return source_offset_list


@pytest.fixture(name="offset_timestamps")
def source_offset_timestamps_fixture():
    """Source offset timestamps fixture"""
    offset_timestamps_list = []
    for _ in range(NSCANS):
        offset_timestamps_list.append(POINTING_TIMESTAMPS)
    return offset_timestamps_list


@pytest.fixture(name="target")
def katpoint_target_fixture():
    """katpoint target fixture"""
    return TARGET


@pytest.fixture(name="vis_array")
def vis_array_fixture(configuration):
    """Visibility fixture"""
    vis_list = []
    for _ in range(NSCANS):
        vis = Visibility.constructor(
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
        vis_list.append(vis)
    return vis_list


@pytest.fixture(name="frequency")
def freqs_fixture():
    """The frequencies of observation fixture"""
    return FREQS


@pytest.fixture(name="frequency_per_chunk")
def freq_per_chunk_fixture():
    """The averaged-frequency per sub-band fixture"""
    return numpy.mean(FREQS.reshape(NUM_CHUNKS, -1), axis=1)


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


@pytest.fixture(name="weights_per_scan")
def weights_per_scan_fixture():
    """The weights of all antennas for each scan fixture"""
    return WEIGHTS_PER_SCAN
