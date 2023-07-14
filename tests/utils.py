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
NCHAN = 2064
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
FREQS = numpy.linspace(899468750.0, 1667486328.125, NCHAN)
CHANNEL_BANDWIDTH = numpy.full(FREQS.shape, 372281.909)

SOURCE = "J1939-6342"
PHASECENTRE = SkyCoord(294.85429167, -63.71266667, unit="deg")

# Complex visibilities
VIS = numpy.full(
    (NTIMES, len(BASELINES), NCHAN, NPOL), numpy.complex128(1.0 + 0.01j)
)
VIS_WEIGHTS = numpy.ones(VIS.shape)
FLAGS = numpy.zeros(VIS.shape)

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
# Has shape (no. of antennas, no. of frequency chunks, no. of scans)
Y_PER_SCAN_GAINS = numpy.array(
    [
        [
            [1.90342356, 2.91675056, 1.76692734, 2.8756133, 1.66467089],
            [1.88963521, 2.95224221, 1.78108412, 2.94932163, 1.70391888],
            [1.73601047, 2.99333841, 1.65488367, 2.95707292, 1.58781564],
            [1.47257442, 2.7601095, 1.44105214, 2.73376194, 1.3639985],
            [1.31403023, 2.72319964, 1.30145646, 2.68968733, 1.21331039],
            [1.31196846, 2.83087968, 1.27494707, 2.78628908, 1.16037217],
            [1.08234348, 2.71612835, 1.01182032, 2.67887823, 0.93855813],
            [0.97005786, 2.67569606, 0.94070432, 2.63011291, 0.83492244],
            [0.76638142, 2.58131818, 0.76553687, 2.54161068, 0.66230642],
            [0.69166017, 2.55042841, 0.71578375, 2.5095374, 0.54812617],
            [0.58581889, 2.38297166, 0.55673979, 2.37419228, 0.47584806],
            [0.48943916, 2.21862832, 0.51476735, 2.23399601, 0.37494279],
            [0.41273965, 2.11046186, 0.3632067, 2.12637667, 0.32763717],
            [0.32610446, 1.88872966, 0.25690884, 1.8910061, 0.25626778],
            [0.26227795, 1.60963546, 0.33270224, 1.61140789, 0.21130938],
            [0.23686117, 1.48558603, 0.32560915, 1.50245514, 0.20040898],
        ],
        [
            [2.03984367, 3.15015261, 1.9600817, 3.12019013, 1.92425644],
            [2.00346717, 3.14152713, 1.88777514, 3.1100368, 1.81060467],
            [1.78649174, 3.05760136, 1.70706521, 3.02817376, 1.63511957],
            [1.53066719, 2.84391254, 1.50622818, 2.81337525, 1.38440562],
            [1.36587841, 2.8027539, 1.3493165, 2.76769451, 1.26292839],
            [1.28812303, 2.88757784, 1.26282182, 2.8340441, 1.19744509],
            [1.09234024, 2.77281529, 1.06036103, 2.74179846, 0.97652844],
            [0.98830529, 2.75932154, 0.94809114, 2.70546087, 0.8655535],
            [0.7843991, 2.66879849, 0.76363643, 2.60270685, 0.67161132],
            [0.71809938, 2.67902497, 0.57308263, 2.62459752, 0.57360027],
            [0.60988761, 2.4500636, 0.4612537, 2.4358956, 0.46228732],
            [0.54864923, 2.38745719, 0.30772473, 2.40649992, 0.40840427],
            [0.52635606, 2.31890984, 0.3268929, 2.32766033, 0.37610606],
            [0.39764672, 2.17928393, 0.34147649, 2.16750812, 0.29066858],
            [0.32531399, 1.89754355, 0.28660548, 1.87990235, 0.23056765],
            [0.2871632, 1.75035925, 0.35852012, 1.74598486, 0.1935672],
        ],
        [
            [2.11195467, 3.27474924, 2.02794061, 3.1904891, 1.90810835],
            [2.08790123, 3.28456663, 1.97300921, 3.23861953, 1.88218012],
            [1.85663606, 3.20208183, 1.77387113, 3.15255391, 1.70870057],
            [1.59314889, 2.94037806, 1.5332561, 2.9074027, 1.44712203],
            [1.36052844, 2.8133108, 1.33535248, 2.77560447, 1.25633326],
            [1.3216746, 2.88119982, 1.29437946, 2.83602786, 1.2052662],
            [1.08886828, 2.76491383, 1.0367058, 2.72830228, 0.9493441],
            [0.95964571, 2.70411259, 0.95089302, 2.6768864, 0.83587829],
            [0.78365524, 2.58159091, 0.72770485, 2.54370196, 0.6800179],
            [0.68733763, 2.53005677, 0.68311974, 2.4941302, 0.59111957],
            [0.59979633, 2.36010179, 0.52062729, 2.36375947, 0.49421673],
            [0.51035304, 2.19267897, 0.4772241, 2.21269178, 0.41011086],
            [0.44784306, 2.09459851, 0.30477012, 2.10529667, 0.30479229],
            [0.32208678, 1.94975382, 0.29401918, 1.9349218, 0.26488129],
            [0.28500011, 1.73836873, 0.28706394, 1.72999625, 0.18606285],
            [0.24502953, 1.57390453, 0.30551896, 1.58195293, 0.22310478],
        ],
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
WEIGHTS_PER_SCAN = numpy.array(
    [
        [
            [
                93.51636687,
                249.48934705,
                96.36004152,
                211.48545063,
                85.01479766,
            ],
            [86.09414759, 205.93731371, 71.4576142, 212.9748493, 78.83113586],
            [
                85.62890565,
                255.15063134,
                79.59426787,
                244.64012668,
                71.76017651,
            ],
            [62.91204414, 218.989472, 57.2478266, 208.17861648, 54.19330992],
            [48.34958306, 213.3413034, 43.11560594, 189.39459377, 41.12562885],
            [
                29.98827743,
                130.02498946,
                26.18312567,
                123.15769026,
                21.87850713,
            ],
            [8.87581444, 58.83686507, 8.50700162, 51.04655672, 5.72062029],
            [8.71491789, 60.625935, 7.81335179, 60.97125737, 6.17035338],
            [14.5537222, 158.22558698, 13.96439104, 152.92477508, 10.59324524],
            [12.59285352, 201.3926917, 13.50759117, 178.82078743, 9.70222125],
            [10.44958779, 173.19898301, 7.66969167, 169.0880667, 6.6090056],
            [7.97507307, 153.7106602, 5.43376424, 153.36313601, 4.8899476],
            [3.81522669, 89.55495294, 2.36373531, 86.68859599, 2.17189041],
            [0.95633484, 33.34974783, 0.75061027, 33.38168893, 0.62366029],
            [2.44709145, 91.07667177, 2.00824831, 89.08641655, 1.4057268],
            [1.90483067, 80.51283555, 2.32557337, 69.88531436, 1.15077523],
        ],
        [
            [
                73.98048258,
                196.26111192,
                76.56396211,
                167.63673153,
                67.20661148,
            ],
            [69.14620551, 159.19884143, 56.83910156, 169.58781329, 61.826596],
            [
                68.32036247,
                201.09654453,
                63.51053093,
                193.31439782,
                56.56451811,
            ],
            [50.23614576, 172.63778776, 45.57394033, 164.55982946, 42.2646635],
            [
                38.77407464,
                167.67829956,
                34.43969639,
                149.53037704,
                32.24176938,
            ],
            [23.96308956, 99.29544459, 20.42674512, 94.83869344, 16.58492698],
            [6.86344285, 45.959635, 6.76300338, 38.0216575, 4.43433112],
            [6.87992807, 48.08069764, 5.99053832, 47.36145168, 4.77759284],
            [11.4927253, 123.36142304, 11.12123415, 120.96423301, 8.39916549],
            [9.90526782, 158.20901368, 10.68150518, 141.21409279, 7.66931798],
            [8.27722908, 136.16675931, 5.99220079, 133.6473229, 5.19200788],
            [6.38133018, 120.53546973, 4.26212075, 120.00239027, 3.78216509],
            [3.09150881, 70.45135913, 1.85996861, 68.23496957, 1.67272359],
            [0.77619557, 24.30264549, 0.59265959, 25.93531726, 0.45208278],
            [2.05171599, 72.54619295, 1.61343963, 70.39159966, 1.02933834],
            [1.6148813, 63.47386602, 1.8311881, 54.84125663, 0.84610111],
        ],
        [
            [80.00561718, 213.34709775, 82.04205904, 178.25319069, 73.0082836],
            [
                73.59652211,
                172.69666636,
                60.87793472,
                180.67991391,
                66.71270901,
            ],
            [73.0525732, 216.39614194, 67.95036697, 207.5974139, 60.87303465],
            [
                53.65006271,
                184.69290168,
                48.76117096,
                175.23701843,
                45.69494121,
            ],
            [41.2713874, 180.56482092, 36.80343576, 159.1542757, 34.7394047],
            [
                25.20597706,
                109.04530686,
                22.20198803,
                102.55787735,
                18.02077444,
            ],
            [6.95874585, 46.42561434, 6.78668116, 40.03770357, 4.65427943],
            [6.96086455, 49.02199242, 6.4693307, 48.66340117, 5.07600924],
            [12.27495105, 133.93242591, 11.94973857, 129.16787453, 8.99263654],
            [10.74333543, 171.71099308, 11.5403494, 152.76971021, 8.27723105],
            [8.92986348, 147.06211738, 6.54210063, 144.74759447, 5.61104663],
            [6.82680813, 130.57922169, 4.63648958, 130.33444485, 4.14705238],
            [3.24732495, 76.49494039, 1.99167561, 73.88279846, 1.81872085],
            [0.8416895, 26.76367386, 0.58617251, 27.03914269, 0.51367238],
            [2.11118624, 78.9643089, 1.71367098, 76.00644704, 1.17069012],
            [1.65785978, 68.39189312, 1.99738032, 59.79220001, 0.96367362],
        ],
    ]
)

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
