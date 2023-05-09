# pylint: disable=too-many-return-statements, inconsistent-return-statements
# pylint: disable=too-few-public-methods
"""
Common Variables and Mock Class Objects used for testing
"""
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
XYZ = numpy.array(
    [
        [5109237.714735, 2006795.661955, -3239109.183708],
        [5109251.156928, 2006811.008353, -3239078.678007],
        [5109238.357021, 2006770.325838, -3239123.769211],
    ]
)
LOCATION = EarthLocation(
    x=Quantity(XYZ[0][0], "m"),
    y=Quantity(XYZ[0][1], "m"),
    z=Quantity(XYZ[0][2], "m"),
)
DIAMETER = numpy.array([25.0, 25.0, 25.0])
STATION = [
    "SKAMID-CORE",
    "SKAMID-CORE",
    "SKAMID-CORE",
]
NAME = ["SKA001 ", "SKA002", "SKA003"]
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
TIMESTAMPS = numpy.array(
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
        8.56000000e08,
        8.56208984e08,
        8.56417969e08,
        8.56626953e08,
        8.56835938e08,
    ]
)
CHANNEL_BANDWIDTH = numpy.array(
    [208984.375, 208984.375, 208984.375, 208984.375, 208984.375]
)
SOURCE = "J1939-6342"
PHASECENTRE = SkyCoord(294.85429167, -63.71266667, unit="deg")

# y-parameter when fitting the primary beam to the visibilities
VIS = numpy.array(
    [
        [
            [
                [0.99983501 + 1.98115282e-17j, 0.99983501 + 1.98115282e-17j],
                [0.99983501 + 6.49309360e-18j, 0.99983501 + 6.49309360e-18j],
                [0.99983501 - 1.34952846e-17j, 0.99983501 - 1.34952846e-17j],
                [0.99983501 - 1.08721621e-19j, 0.99983501 - 1.08721621e-19j],
                [0.99983501 + 3.15615312e-18j, 0.99983501 + 3.15615312e-18j],
            ],
            [
                [0.99884993 + 4.43728864e-02j, 0.99884993 + 4.43728864e-02j],
                [0.99973571 + 1.40915830e-02j, 0.99973571 + 1.40915830e-02j],
                [0.99732262 + 7.08354264e-02j, 0.99732262 + 7.08354264e-02j],
                [0.99866235 + 4.84113507e-02j, 0.99866235 + 4.84113507e-02j],
                [0.99972689 + 1.47060901e-02j, 0.99972689 + 1.47060901e-02j],
            ],
            [
                [0.9910832 + 1.32000595e-01j, 0.9910832 + 1.32000595e-01j],
                [0.99167794 - 1.27455637e-01j, 0.99167794 - 1.27455637e-01j],
                [0.99982882 - 3.52006848e-03j, 0.99982882 - 3.52006848e-03j],
                [0.99943554 + 2.82619726e-02j, 0.99943554 + 2.82619726e-02j],
                [0.99977702 + 1.07692042e-02j, 0.99977702 + 1.07692042e-02j],
            ],
            [
                [0.99983501 + 1.98115282e-17j, 0.99983501 + 1.98115282e-17j],
                [0.99983501 + 6.49309360e-18j, 0.99983501 + 6.49309360e-18j],
                [0.99983501 - 1.34952846e-17j, 0.99983501 - 1.34952846e-17j],
                [0.99983501 - 1.08721621e-19j, 0.99983501 - 1.08721621e-19j],
                [0.99983501 + 3.15615312e-18j, 0.99983501 + 3.15615312e-18j],
            ],
            [
                [0.99983501 - 2.12095048e-17j, 0.99983501 - 2.12095048e-17j],
                [0.99983501 - 1.94808388e-19j, 0.99983501 - 1.94808388e-19j],
                [0.99983501 - 2.14729106e-17j, 0.99983501 - 2.14729106e-17j],
                [0.99983501 - 1.05204449e-18j, 0.99983501 - 1.05204449e-18j],
                [0.99983501 - 5.57131620e-18j, 0.99983501 - 5.57131620e-18j],
            ],
            [
                [0.99596494 + 8.78860503e-02j, 0.99596494 + 8.78860503e-02j],
                [0.98978311 - 1.41419590e-01j, 0.98978311 - 1.41419590e-01j],
                [0.99706709 - 7.43462071e-02j, 0.99706709 - 7.43462071e-02j],
                [0.9996317 - 2.01631822e-02j, 0.9996317 - 2.01631822e-02j],
                [0.99982727 - 3.93719831e-03j, 0.99982727 - 3.93719831e-03j],
            ],
        ],
        [
            [
                [0.99983501 + 2.70348515e-17j, 0.99983501 + 2.70348515e-17j],
                [0.99983501 + 2.66375194e-18j, 0.99983501 + 2.66375194e-18j],
                [0.99983501 - 4.13879613e-18j, 0.99983501 - 4.13879613e-18j],
                [0.99983501 - 6.65996715e-19j, 0.99983501 - 6.65996715e-19j],
                [0.99983501 + 1.90099092e-18j, 0.99983501 + 1.90099092e-18j],
            ],
            [
                [0.99884993 + 4.43731360e-02j, 0.99884993 + 4.43731360e-02j],
                [0.99973571 + 1.40916621e-02j, 0.99973571 + 1.40916621e-02j],
                [0.99732262 + 7.08358213e-02j, 0.99732262 + 7.08358213e-02j],
                [0.99866229 + 4.84116226e-02j, 0.99866229 + 4.84116226e-02j],
                [0.99972689 + 1.47061730e-02j, 0.99972689 + 1.47061730e-02j],
            ],
            [
                [0.99108315 + 1.32001325e-01j, 0.99108315 + 1.32001325e-01j],
                [0.99167788 - 1.27456352e-01j, 0.99167788 - 1.27456352e-01j],
                [0.99982882 - 3.52008827e-03j, 0.99982882 - 3.52008827e-03j],
                [0.99943554 + 2.82621309e-02j, 0.99943554 + 2.82621309e-02j],
                [0.99977702 + 1.07692648e-02j, 0.99977702 + 1.07692648e-02j],
            ],
            [
                [0.99983501 + 2.70348515e-17j, 0.99983501 + 2.70348515e-17j],
                [0.99983501 + 2.66375194e-18j, 0.99983501 + 2.66375194e-18j],
                [0.99983501 - 4.13879613e-18j, 0.99983501 - 4.13879613e-18j],
                [0.99983501 - 6.65996715e-19j, 0.99983501 - 6.65996715e-19j],
                [0.99983501 + 1.90099092e-18j, 0.99983501 + 1.90099092e-18j],
            ],
            [
                [0.99983501 - 2.50252245e-17j, 0.99983501 - 2.50252245e-17j],
                [0.99983501 + 5.94204242e-18j, 0.99983501 + 5.94204242e-18j],
                [0.99983501 + 1.04320793e-17j, 0.99983501 + 1.04320793e-17j],
                [0.99983501 - 1.25446996e-18j, 0.99983501 - 1.25446996e-18j],
                [0.99983501 + 6.83609851e-18j, 0.99983501 + 6.83609851e-18j],
            ],
            [
                [0.99596488 + 8.78865495e-02j, 0.99596488 + 8.78865495e-02j],
                [0.98978299 - 1.41420394e-01j, 0.98978299 - 1.41420394e-01j],
                [0.99706703 - 7.43466243e-02j, 0.99706703 - 7.43466243e-02j],
                [0.9996317 - 2.01632958e-02j, 0.9996317 - 2.01632958e-02j],
                [0.99982727 - 3.93722020e-03j, 0.99982727 - 3.93722020e-03j],
            ],
        ],
        [
            [
                [0.99983501 + 7.25972500e-18j, 0.99983501 + 7.25972500e-18j],
                [0.99983501 - 2.25842247e-20j, 0.99983501 - 2.25842247e-20j],
                [0.99983501 + 1.07256788e-17j, 0.99983501 + 1.07256788e-17j],
                [0.99983501 - 3.37137783e-20j, 0.99983501 - 3.37137783e-20j],
                [0.99983501 + 3.54531348e-18j, 0.99983501 + 3.54531348e-18j],
            ],
            [
                [0.99884987 + 4.43733856e-02j, 0.99884987 + 4.43733856e-02j],
                [0.99973571 + 1.40917422e-02j, 0.99973571 + 1.40917422e-02j],
                [0.99732256 + 7.08362237e-02j, 0.99732256 + 7.08362237e-02j],
                [0.99866229 + 4.84118946e-02j, 0.99866229 + 4.84118946e-02j],
                [0.99972689 + 1.47062559e-02j, 0.99972689 + 1.47062559e-02j],
            ],
            [
                [0.99108303 + 1.32002071e-01j, 0.99108303 + 1.32002071e-01j],
                [0.99167776 - 1.27457067e-01j, 0.99167776 - 1.27457067e-01j],
                [0.99982882 - 3.52010806e-03j, 0.99982882 - 3.52010806e-03j],
                [0.99943548 + 2.82622911e-02j, 0.99943548 + 2.82622911e-02j],
                [0.99977702 + 1.07693253e-02j, 0.99977702 + 1.07693253e-02j],
            ],
            [
                [0.99983501 + 7.25972500e-18j, 0.99983501 + 7.25972500e-18j],
                [0.99983501 - 2.25842247e-20j, 0.99983501 - 2.25842247e-20j],
                [0.99983501 + 1.07256788e-17j, 0.99983501 + 1.07256788e-17j],
                [0.99983501 - 3.37137783e-20j, 0.99983501 - 3.37137783e-20j],
                [0.99983501 + 3.54531348e-18j, 0.99983501 + 3.54531348e-18j],
            ],
            [
                [0.99983501 - 1.82882255e-17j, 0.99983501 - 1.82882255e-17j],
                [0.99983501 - 6.53426817e-18j, 0.99983501 - 6.53426817e-18j],
                [0.99983501 - 3.99674316e-18j, 0.99983501 - 3.99674316e-18j],
                [0.99983501 + 9.41664270e-19j, 0.99983501 + 9.41664270e-19j],
                [0.99983501 + 5.40397839e-18j, 0.99983501 + 5.40397839e-18j],
            ],
            [
                [0.99596483 + 8.78870413e-02j, 0.99596483 + 8.78870413e-02j],
                [0.98978287 - 1.41421184e-01j, 0.98978287 - 1.41421184e-01j],
                [0.99706703 - 7.43470415e-02j, 0.99706703 - 7.43470415e-02j],
                [0.9996317 - 2.01634094e-02j, 0.9996317 - 2.01634094e-02j],
                [0.99982727 - 3.93724255e-03j, 0.99982727 - 3.93724255e-03j],
            ],
        ],
        [
            [
                [0.99983501 - 1.96523886e-17j, 0.99983501 - 1.96523886e-17j],
                [0.99983501 - 5.99192720e-18j, 0.99983501 - 5.99192720e-18j],
                [0.99983501 + 1.13798959e-17j, 0.99983501 + 1.13798959e-17j],
                [0.99983501 - 5.24870862e-19j, 0.99983501 - 5.24870862e-19j],
                [0.99983501 + 8.51691977e-20j, 0.99983501 + 8.51691977e-20j],
            ],
            [
                [0.99884987 + 4.43736352e-02j, 0.99884987 + 4.43736352e-02j],
                [0.99973571 + 1.40918214e-02j, 0.99973571 + 1.40918214e-02j],
                [0.99732256 + 7.08366185e-02j, 0.99732256 + 7.08366185e-02j],
                [0.99866229 + 4.84121665e-02j, 0.99866229 + 4.84121665e-02j],
                [0.99972689 + 1.47063388e-02j, 0.99972689 + 1.47063388e-02j],
            ],
            [
                [0.99108291 + 1.32002816e-01j, 0.99108291 + 1.32002816e-01j],
                [0.9916777 - 1.27457783e-01j, 0.9916777 - 1.27457783e-01j],
                [0.99982882 - 3.52012808e-03j, 0.99982882 - 3.52012808e-03j],
                [0.99943548 + 2.82624494e-02j, 0.99943548 + 2.82624494e-02j],
                [0.99977702 + 1.07693858e-02j, 0.99977702 + 1.07693858e-02j],
            ],
            [
                [0.99983501 - 1.96523886e-17j, 0.99983501 - 1.96523886e-17j],
                [0.99983501 - 5.99192720e-18j, 0.99983501 - 5.99192720e-18j],
                [0.99983501 + 1.13798959e-17j, 0.99983501 + 1.13798959e-17j],
                [0.99983501 - 5.24870862e-19j, 0.99983501 - 5.24870862e-19j],
                [0.99983501 + 8.51691977e-20j, 0.99983501 + 8.51691977e-20j],
            ],
            [
                [0.99983501 + 1.29103074e-17j, 0.99983501 + 1.29103074e-17j],
                [0.99983501 - 5.86099774e-18j, 0.99983501 - 5.86099774e-18j],
                [0.99983501 + 9.82495270e-18j, 0.99983501 + 9.82495270e-18j],
                [0.99983501 - 1.35855291e-19j, 0.99983501 - 1.35855291e-19j],
                [0.99983501 - 1.13012238e-18j, 0.99983501 - 1.13012238e-18j],
            ],
            [
                [0.99596483 + 8.78875330e-02j, 0.99596483 + 8.78875330e-02j],
                [0.98978275 - 1.41421974e-01j, 0.98978275 - 1.41421974e-01j],
                [0.99706697 - 7.43474588e-02j, 0.99706697 - 7.43474588e-02j],
                [0.9996317 - 2.01635230e-02j, 0.9996317 - 2.01635230e-02j],
                [0.99982727 - 3.93726444e-03j, 0.99982727 - 3.93726444e-03j],
            ],
        ],
        [
            [
                [0.99983501 + 1.73415570e-17j, 0.99983501 + 1.73415570e-17j],
                [0.99983501 + 5.81243314e-18j, 0.99983501 + 5.81243314e-18j],
                [0.99983501 + 1.78332737e-18j, 0.99983501 + 1.78332737e-18j],
                [0.99983501 - 4.43625396e-20j, 0.99983501 - 4.43625396e-20j],
                [0.99983501 - 4.27771284e-18j, 0.99983501 - 4.27771284e-18j],
            ],
            [
                [0.99884987 + 4.43738848e-02j, 0.99884987 + 4.43738848e-02j],
                [0.99973571 + 1.40919005e-02j, 0.99973571 + 1.40919005e-02j],
                [0.9973225 + 7.08370209e-02j, 0.9973225 + 7.08370209e-02j],
                [0.99866229 + 4.84124385e-02j, 0.99866229 + 4.84124385e-02j],
                [0.99972689 + 1.47064216e-02j, 0.99972689 + 1.47064216e-02j],
            ],
            [
                [0.99108285 + 1.32003546e-01j, 0.99108285 + 1.32003546e-01j],
                [0.99167758 - 1.27458498e-01j, 0.99167758 - 1.27458498e-01j],
                [0.99982882 - 3.52014787e-03j, 0.99982882 - 3.52014787e-03j],
                [0.99943548 + 2.82626096e-02j, 0.99943548 + 2.82626096e-02j],
                [0.99977702 + 1.07694464e-02j, 0.99977702 + 1.07694464e-02j],
            ],
            [
                [0.99983501 + 1.73415570e-17j, 0.99983501 + 1.73415570e-17j],
                [0.99983501 + 5.81243314e-18j, 0.99983501 + 5.81243314e-18j],
                [0.99983501 + 1.78332737e-18j, 0.99983501 + 1.78332737e-18j],
                [0.99983501 - 4.43625396e-20j, 0.99983501 - 4.43625396e-20j],
                [0.99983501 - 4.27771284e-18j, 0.99983501 - 4.27771284e-18j],
            ],
            [
                [0.99983501 - 2.58412266e-17j, 0.99983501 - 2.58412266e-17j],
                [0.99983501 + 2.27209516e-18j, 0.99983501 + 2.27209516e-18j],
                [0.99983501 + 1.61473729e-17j, 0.99983501 + 1.61473729e-17j],
                [0.99983501 + 7.30486714e-19j, 0.99983501 + 7.30486714e-19j],
                [0.99983501 + 1.90981569e-18j, 0.99983501 + 1.90981569e-18j],
            ],
            [
                [0.99596477 + 8.78880322e-02j, 0.99596477 + 8.78880322e-02j],
                [0.98978263 - 1.41422763e-01j, 0.98978263 - 1.41422763e-01j],
                [0.99706692 - 7.43478835e-02j, 0.99706692 - 7.43478835e-02j],
                [0.9996317 - 2.01636367e-02j, 0.9996317 - 2.01636367e-02j],
                [0.99982727 - 3.93728679e-03j, 0.99982727 - 3.93728679e-03j],
            ],
        ],
    ]
)

# y-parameter when fitting the primary beam to the gain amplitudes
GAIN = numpy.array(
    [
        [
            [
                [
                    [1.98762708 + 0.00468363j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.98722167 + 0.01273955j],
                ]
            ],
            [
                [
                    [1.9805374 - 0.00259519j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.96818067 + 0.00610415j],
                ]
            ],
            [
                [
                    [1.99001485 + 0.02336892j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.94290814 + 0.02793795j],
                ]
            ],
        ],
        [
            [
                [
                    [2.00749956 + 0.46457728j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.96016786 + 0.43255224j],
                ]
            ],
            [
                [
                    [1.98391337 + 0.41575343j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.92633737 + 0.4720727j],
                ]
            ],
            [
                [
                    [1.99703873 - 0.54565571j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.93822325 - 0.44815771j],
                ]
            ],
        ],
        [
            [
                [
                    [2.0014137 - 0.07993824j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 2.00094249 - 0.03064635j],
                ]
            ],
            [
                [
                    [1.99891215 + 0.08190329j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.9988133 + 0.01560186j],
                ]
            ],
            [
                [
                    [1.99945753 + 0.03106503j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.99788286 - 0.0058616j],
                ]
            ],
        ],
        [
            [
                [
                    [2.00060917 - 0.16212387j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.99910105 - 0.06334603j],
                ]
            ],
            [
                [
                    [1.99874346 + 0.15957328j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.99774502 + 0.02463885j],
                ]
            ],
            [
                [
                    [2.00031171 + 0.06336577j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.99646371 - 0.01033008j],
                ]
            ],
        ],
        [
            [
                [
                    [1.90125428 + 0.45048568j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.85299348 - 0.52040699j],
                ]
            ],
            [
                [
                    [1.93956563 + 0.40819864j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 2.02733306 + 0.19520254j],
                ]
            ],
            [
                [
                    [1.97188759 + 0.32419697j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.96823741 + 0.32789823j],
                ]
            ],
        ],
    ]
)

GAIN_WEIGHT = numpy.array(
    [
        [
            [[[751.35095037, 0.0], [0.0, 730.97438541]]],
            [[[765.57530185, 0.0], [0.0, 739.96660188]]],
            [[[737.14404368, 0.0], [0.0, 741.61800441]]],
        ],
        [
            [[[247.60881609, 0.0], [0.0, 249.77351994]]],
            [[[248.39477351, 0.0], [0.0, 246.25917495]]],
            [[[234.7392233, 0.0], [0.0, 243.52235635]]],
        ],
        [
            [[[726.81274494, 0.0], [0.0, 642.53790686]]],
            [[[728.60464467, 0.0], [0.0, 632.35684225]]],
            [[[707.82600997, 0.0], [0.0, 637.63494049]]],
        ],
        [
            [[[725.94251634, 0.0], [0.0, 643.78875462]]],
            [[[727.58531841, 0.0], [0.0, 633.9413259]]],
            [[[707.83828707, 0.0], [0.0, 639.10712954]]],
        ],
        [
            [[[808.89395889, 0.0], [0.0, 702.1304842]]],
            [[[801.54047147, 0.0], [0.0, 686.4077971]]],
            [[[786.41670528, 0.0], [0.0, 699.14209769]]],
        ],
    ]
)


GAIN_RESIDUAL = numpy.array(
    [
        [[[2.18231239, 0.0], [0.0, 2.37574335]]],
        [[[0.82453787, 0.0], [0.0, 0.866436]]],
        [[[0.18392438, 0.0], [0.0, 0.17862158]]],
        [[[0.19306114, 0.0], [0.0, 0.18525042]]],
        [[[0.80434434, 0.0], [0.0, 0.7954749]]],
    ]
)


# y-parameter when fitting the primary beam to the visibilities
# Weights - used as standard deviation on the y-parameter when
# fitting the primary beams to visibility amplitudes
VIS_WEIGHTS = numpy.ones((5, 6, 5, 2))
FLAGS = numpy.zeros((5, 6, 5, 2))


# Dish coordinates for beam_fitting- the x parameter to be used in the fitting
DISH_COORD_AZ = numpy.array(
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

DISH_COORD_EL = numpy.array(
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
        if columnname == "SOURCE_OFFSET":
            return numpy.dstack((DISH_COORD_AZ, DISH_COORD_EL))

        if columnname == "TIME":
            return TIMESTAMPS
