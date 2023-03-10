# pylint: disable=too-many-return-statements, inconsistent-return-statements
# pylint: disable=too-few-public-methods, duplicate-code
"""
Common Variables and Mock Class Objects used for testing
"""
import numpy

from ska_sdp_wflow_pointing_offset import construct_antennas

NTIMES = 5
NANTS = 3
NCHAN = 5
NCORR = 15
NPOL = 2
XYZ = numpy.array(
    [
        [5109237.714735, 2006795.661955, -3239109.183708],
        [5109251.156928, 2006811.008353, -3239078.678007],
        [5109238.357021, 2006770.325838, -3239123.769211],
    ]
)
DIAMETER = numpy.array([25.0, 25.0, 25.0])
STATION = [
    "SKAMID-CORE",
    "SKAMID-CORE",
    "SKAMID-CORE",
]
ANTS = construct_antennas(XYZ, DIAMETER, STATION)
# Define the parameters for fit primary beam function
CORR_TYPE = ["XX", "YY"]
TIMESTAMPS = numpy.array(
    [
        1.67272797e09,
        1.67272798e09,
        1.67272800e09,
        1.67272801e09,
        1.67272803e09,
    ]
)
FREQS = numpy.array(
    [
        8.56000000e08,
        8.56208984e08,
        8.56417969e08,
        8.56626953e08,
        8.56835938e08,
    ]
)

# Visibility for beam_fitting- the y parameter to be used in the fitting
VIS = numpy.array(
    [
        [
            10431.873,
            9127.823,
            10141.914,
            59011.547,
            10860.39,
            9806.72,
            9204.591,
            17989.33,
            30690.541,
            14414.348,
            15283.417,
            14005.097,
            9860.686,
            26317.227,
            9236.236,
        ],
        [
            10431.873,
            9127.823,
            10141.914,
            59011.547,
            10860.39,
            9806.72,
            9204.591,
            17989.33,
            30690.541,
            14414.348,
            15283.417,
            14005.097,
            9860.686,
            26317.227,
            9236.236,
        ],
    ]
)

# Weights - used as standard deviation on the y-parameter
VIS_WEIGHT = numpy.array(
    [
        [
            0.16797385,
            0.17385559,
            0.16107331,
            0.19380789,
            0.11699289,
            0.1938036,
            0.17419179,
            0.18623605,
            0.16278373,
            0.15633371,
            0.17856638,
            0.18040745,
            0.15366295,
            0.15283653,
            0.16469233,
        ],
        [
            0.15729496,
            0.16163893,
            0.16258055,
            0.1790921,
            0.11462438,
            0.19291812,
            0.1803138,
            0.17485328,
            0.17238507,
            0.1655575,
            0.17291346,
            0.18430558,
            0.17445499,
            0.10147141,
            0.13969643,
        ],
    ]
)
DISH_COORD_X = numpy.array(
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

DISH_COORD_Y = numpy.array(
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


class MockBaseTable:
    """
    Mock Base Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "TIME":
            return TIMESTAMPS

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
            return numpy.array(VIS_WEIGHT.reshape((NCORR, NPOL)))


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
            return ["ALT-AZ", "ALT-AZ", "ALT-AZ"]

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
            return numpy.array(
                [
                    [0.00000000e00, 0.00000000e00, 0.00000000e00],
                    [2.18848512e-03, 0.00000000e00, 0.00000000e00],
                    [-3.02790361e-03, 0.00000000e00, 0.00000000e00],
                ]
            )

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


class MockSourceTable:
    """
    Source Table Class
    """

    def getcol(self, columnname=None):
        """
        Get column name
        """
        if columnname == "NAME":
            return ["J1939-6342"]
        if columnname == "DIRECTION":
            return numpy.array([[5.1461782, -1.11199581]])


class MockRDBInput:
    """
    Mock RDB Input Class
    """

    @property
    def timestamps(self):
        """Timestamps"""
        return TIMESTAMPS

    @property
    def target_projection(self):
        """Target projection"""
        return "ARC"

    @property
    def ants(self):
        """Katpoint antennas"""
        return ANTS

    @property
    def target_x(self):
        """Target x coordinates"""
        return DISH_COORD_X

    @property
    def target_y(self):
        """Target y coordinates"""
        return DISH_COORD_Y
