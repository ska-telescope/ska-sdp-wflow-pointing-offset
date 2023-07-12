# pylint: disable=too-many-return-statements,inconsistent-return-statements
# pylint: disable=too-few-public-methods
"""
Common Variables and Mock Class Objects used for testing
"""
import katpoint
import numpy
import pandas
from astropy.coordinates import EarthLocation, SkyCoord
from astropy.units import Quantity
from ska_sdp_datamodels.science_data_model.polarisation_model import (
    PolarisationFrame,
)
from ska_sdp_datamodels.visibility.vis_utils import generate_baselines

from ska_sdp_wflow_pointing_offset import construct_antennas

NTIMES = 5
NANTS = 3
NCHAN = 5
NCORR = 15
NPOL = 2
BEAMWIDTH_FACTOR = (0.96, 1.098)
THRESH_WIDTH = 1.5
XYZ = numpy.array(
    [
        [5109271.497354163, 2006808.8930278125, -3239130.7361407224],
        [5109284.8540775385, 2006824.2217235335, -3239100.126460417],
        [5109272.199343496, 2006783.5460499495, -3239145.330041681],
    ]
)
LOCATION = EarthLocation(
    x=Quantity(XYZ[0][0], "m"),
    y=Quantity(XYZ[0][1], "m"),
    z=Quantity(XYZ[0][2], "m"),
)
DIAMETER = numpy.array([13.5, 13.5, 13.5])
STATION = [
    "M001",
    "M002",
    "M003",
]
NAME = ["M001", "M002", "M003"]
MOUNT = ["ALT-AZ", "ALT-AZ", "ALT-AZ"]
OFFSET = numpy.array(
    [
        [0.00000000e00, 0.00000000e00, 0.00000000e00],
        [2.18848512e-03, 0.00000000e00, 0.00000000e00],
        [-3.02790361e-03, 0.00000000e00, 0.00000000e00],
    ]
)
ANTS = construct_antennas(XYZ, DIAMETER, STATION)
BASELINES = pandas.MultiIndex.from_tuples(
    generate_baselines(NANTS), names=("antenna1", "antenna2")
)
UVW = numpy.array(
    [
        [
            [0.0, 0.0, 0.0],
            [-397.89452612, 584.1169983, -153.35096251],
            [-1357.78172302, 56.39427491, -30.15833161],
            [-33.08582193, -422.93637971, 107.28705751],
            [0.0, 0.0, 0.0],
            [-959.8871969, -527.7227234, 123.1926309],
        ],
        [
            [0.0, 0.0, 0.0],
            [-397.67291131, 584.32154768, -153.14641314],
            [-1357.76787287, 57.09247337, -29.46013315],
            [-33.24812717, -422.9193245, 107.30411272],
            [0.0, 0.0, 0.0],
            [-960.09496157, -527.2290743, 123.68627999],
        ],
        [
            [0.0, 0.0, 0.0],
            [-397.45108619, 584.52598303, -152.94197778],
            [-1357.75330468, 57.79066453, -28.76194199],
            [-33.41041483, -422.90218584, 107.32125138],
            [0.0, 0.0, 0.0],
            [-960.30221849, -526.7353185, 124.18003579],
        ],
        [
            [0.0, 0.0, 0.0],
            [-397.22905088, 584.73030427, -152.73765654],
            [-1357.73801843, 58.48884802, -28.0637585],
            [-33.57268481, -422.88496373, 107.33847349],
            [0.0, 0.0, 0.0],
            [-960.50896755, -526.24145625, 124.67389804],
        ],
        [
            [0.0, 0.0, 0.0],
            [-397.0068055, 584.93451128, -152.53344954],
            [-1357.72201414, 59.18702345, -27.36558307],
            [-33.73493705, -422.86765818, 107.35577904],
            [0.0, 0.0, 0.0],
            [-960.71520865, -525.74748782, 125.16786647],
        ],
    ]
)


# Define the parameters for fit primary beam function
CORR_TYPE = ["XX", "YY"]
POLARISATION_FRAME = PolarisationFrame("linearnp")
VIS_TIMESTAMPS = numpy.array(
    [5.17944476e09, 5.17944477e09, 5.17944480e09, 5.17944480e09, 5.17944483e09]
)
POINTING_TIMESTAMPS = numpy.array(
    [
        1.67272797e09,
        1.67272798e09,
        1.67272800e09,
        1.67272801e09,
        1.67272803e09,
    ]
)
INTEGRATION_TIME = numpy.array(
    [7.99661697, 7.99661697, 7.99661697, 7.99661697, 7.99661697]
)
INTERVAL = numpy.array(
    [7.99661732, 7.99661732, 23.98985195, 7.99661636, 23.98985195]
)
FREQS = numpy.array(
    [
        1283477539.0625,
        1283686523.4375,
        1283895507.8125,
        1284104492.1875,
        1284313476.5625,
    ]
)
CHANNEL_BANDWIDTH = numpy.array(
    [208984.375, 208984.375, 208984.375, 208984.375, 208984.375]
)
SOURCE = "J1939-6342"
PHASECENTRE = SkyCoord(294.85429167, -63.71266667, unit="deg")

# Complex visibilities
VIS = numpy.full(
    (NTIMES, len(BASELINES), NCHAN, NPOL), numpy.complex128(1.0 + 0.01j)
)

# x-parameter (antenna pointings) required for fitting
X_PER_SCAN = numpy.array(
    [
        [
            [7.25041746e-06, -9.99999151e-01],
            [7.25041746e-06, -9.99999151e-01],
            [7.25041746e-06, -9.99999151e-01],
        ],
        [
            [1.57611535e-06, 3.33334665e-01],
            [1.57611535e-06, 3.33334665e-01],
            [1.57611535e-06, 3.33334665e-01],
        ],
        [
            [4.01609741e-06, 1.00000129e00],
            [4.01609741e-06, 1.00000129e00],
            [4.01609741e-06, 1.00000129e00],
        ],
        [
            [3.33337117e-01, 2.12096489e-06],
            [3.33337117e-01, 2.12096489e-06],
            [3.33337117e-01, 2.12096489e-06],
        ],
        [
            [1.00000156e00, 1.12394609e-06],
            [1.00000156e00, 1.12394609e-06],
            [1.00000156e00, 1.12394609e-06],
        ],
    ]
)

# y-parameter when fitting the primary beam to the gain amplitudes
Y_PER_SCAN_GAINS = numpy.array(
    [
        [1.12025963, 2.53539831, 1.07894708, 2.51238993, 1.00556359],
        [1.15828006, 2.62020173, 1.1001975, 2.59177655, 1.04347304],
        [1.18702611, 2.60365584, 1.13277653, 2.57780277, 1.07168091],
    ]
)

# y-parameter when fitting the primary beam to the visibility amplitudes
Y_PER_SCAN_VIS = numpy.array(
    [
        [257.74959364, 268.96652217, 263.62241226, 267.37058841, 263.84486972],
        [291.83644266, 308.56168876, 311.82873557, 306.63003675, 315.50306793],
        [277.73365336, 286.87047706, 280.74303187, 280.82932103, 283.34789401],
    ]
)

# Weights to be used for computing standard deviation on the gain amplitudes
WEIGHTS_PER_SCAN = numpy.full(numpy.shape(Y_PER_SCAN_GAINS), 0.1)

# y-parameter when fitting the primary beam to the visibilities
# Weights - used as standard deviation on the y-parameter when
# fitting the primary beams to visibility amplitudes
VIS_WEIGHTS = numpy.ones((5, 6, 5, 2))
FLAGS = numpy.zeros((5, 6, 5, 2))


# Requested pointings in azel (degrees)
REQUESTED_POINTING_AZ = numpy.array(
    [
        [148.9414995, 148.94205178, 148.94271892],
        [148.94172025, 148.94236573, 148.94355854],
        [148.94101771, 148.94200575, 148.94254095],
        [148.94171501, 148.94121957, 148.94304378],
        [148.94140716, 148.94244255, 148.94256353],
    ]
)

REQUESTED_POINTING_EL = numpy.array(
    [
        [33.39730196, 33.41221842, 34.12342723],
        [33.3971681, 33.41170513, 34.12257392],
        [34.06417534, 34.07836893, 34.79018015],
        [34.06363578, 34.07853663, 34.78971391],
        [34.73060623, 34.74537779, 35.45614139],
    ]
)

# Actual pointings in azel (degrees)
ACTUAL_POINTING_AZ = numpy.array(
    [
        [148.94151627, 148.94209042, 148.94269345],
        [148.9416127, 148.94223792, 148.9435879],
        [148.94151282, 148.94186983, 148.94285118],
        [148.94127324, 148.94149587, 148.94311848],
        [148.94128754, 148.94246971, 148.94286926],
    ]
)

ACTUAL_POINTING_EL = numpy.array(
    [
        [34.39740428, 34.41229524, 35.12337574],
        [34.39719755, 34.4118988, 35.12285761],
        [34.39757858, 34.41206149, 35.12348981],
        [34.39708119, 34.41189889, 35.12313388],
        [34.39734882, 34.41193127, 35.12321936],
    ]
)

# Source offset (difference between in actual and requested pointings)
# in degrees
SOURCE_OFFSET_AZ = numpy.array(
    [
        [
            -1.67656219e-05,
            -3.86416795e-05,
            2.54736615e-05,
        ],
        [
            1.07554380e-04,
            1.27813267e-04,
            -2.93635031e-05,
        ],
        [
            -4.95111837e-04,
            1.35920940e-04,
            -3.10228964e-04,
        ],
        [
            4.41771802e-04,
            -2.76304939e-04,
            -7.46971279e-05,
        ],
        [
            1.19623691e-04,
            -2.71621773e-05,
            -3.05732096e-04,
        ],
    ]
)

SOURCE_OFFSET_EL = numpy.array(
    [
        [
            -1.00010232,
            -1.00007682,
            -0.99994851,
        ],
        [
            -1.00002945,
            -1.00019367,
            -1.00028369,
        ],
        [
            -0.33340324,
            -0.33369256,
            -0.33330966,
        ],
        [
            -0.33344541,
            -0.33336226,
            -0.33341997,
        ],
        [0.33325741, 0.33344652, 0.33292203],
    ]
)


# Pointing calibrator position
ACTUAL_SOURCE = numpy.array([[5.14618, -1.112], [0, 0]])
TARGET = katpoint.construct_radec_target(
    ra=ACTUAL_SOURCE[0][0], dec=ACTUAL_SOURCE[0][1]
)


class MockBaseTable:
    """
    Mock Base Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "TIME":
            return VIS_TIMESTAMPS

        if columnname == "INTERVAL":
            return numpy.array([10.0])

        if columnname == "CPARAM":
            return numpy.ones((NTIMES, NANTS, NCHAN, 1))

        if columnname == "ANTENNA1":
            return numpy.array([0, 1, 2])

        if columnname == "SPECTRAL_WINDOW_ID":
            return numpy.array([0, 1])

        if columnname == "DATA":
            vis_3d = VIS[:, numpy.newaxis, :].repeat(NCHAN, axis=1)
            return numpy.array(vis_3d.reshape((NCORR, NCHAN, NPOL)))

        if columnname == "WEIGHT":
            return numpy.array(VIS_WEIGHTS.reshape((NCORR, NPOL)))


class MockSpectralWindowTable:
    """
    Mock Spectral Window Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "CHAN_FREQ":
            return FREQS

        if columnname == "NUM_CHAN":
            return numpy.array([NCHAN])


class MockAntennaTable:
    """
    Mock Antenna Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name from MS File
        """
        if columnname == "NAME":
            return ["ANT1", "ANT2", "ANT3"]

        if columnname == "MOUNT":
            return MOUNT

        if columnname == "DISH_DIAMETER":
            return DIAMETER

        if columnname == "POSITION":
            return numpy.array(
                [
                    [-1601162.0, -5042003.0, 3554915.0],
                    [-1601192.0190292, -5042007.78341262, 3554960.73493029],
                    [-1601147.19047704, -5042040.12425644, 3554894.80919799],
                ]
            )

        if columnname == "OFFSET":
            return OFFSET

        if columnname == "STATION":
            return STATION


class MockPolarisationTable:
    """
    Mock Polarisation Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "CORR_TYPE":
            return numpy.array([9, 12])


class MockPointingTable:
    """
    Mock Pointing Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "TARGET":
            return numpy.dstack((REQUESTED_POINTING_AZ, REQUESTED_POINTING_EL))

        if columnname == "DIRECTION":
            return numpy.dstack((ACTUAL_POINTING_AZ, ACTUAL_POINTING_EL))

        if columnname == "SOURCE_OFFSET":
            return numpy.dstack((SOURCE_OFFSET_AZ, SOURCE_OFFSET_EL))

        if columnname == "TIME":
            return POINTING_TIMESTAMPS


class MockSourceTable:
    """
    Mock Source Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "DIRECTION":
            return ACTUAL_SOURCE
