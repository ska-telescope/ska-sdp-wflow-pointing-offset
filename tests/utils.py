# pylint: disable=too-many-return-statements,inconsistent-return-statements
# pylint: disable=too-few-public-methods,too-many-lines
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
THRESH_WIDTH = 1.5
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
NAME = ["SKA001", "SKA002", "SKA003"]
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
                [
                    4.34861035e02 + 1.60001478e00j,
                    -5.77202641e-02 + 7.04816705e-02j,
                ],
                [
                    4.10096879e02 + 8.49074106e-01j,
                    5.42008527e-01 - 4.40324848e-01j,
                ],
                [
                    4.29214146e02 + 1.20180603e00j,
                    2.39964395e-01 - 2.83299966e-01j,
                ],
                [
                    4.25437399e02 + 1.12330463e00j,
                    2.83507853e-01 + 3.92359314e-01j,
                ],
                [
                    4.44085182e02 + 1.89910984e00j,
                    2.67135567e-01 + 1.43269312e00j,
                ],
            ],
            [
                [
                    1.33279901e01 + 1.48054741e00j,
                    3.50839784e-01 - 8.22523133e-01j,
                ],
                [
                    1.24892981e01 + 2.56936228e00j,
                    9.31600162e-01 - 9.42664234e-01j,
                ],
                [
                    1.33533124e01 + 1.52119246e00j,
                    -1.83390917e-02 - 1.24279447e00j,
                ],
                [
                    1.39213454e01 + 7.80855506e-01j,
                    1.14176087e00 - 7.48860463e-01j,
                ],
                [
                    1.33892890e01 + 1.48611747e00j,
                    -1.66165682e-01 + 1.18491346e-01j,
                ],
            ],
            [
                [
                    3.76208102e02 - 2.11693487e00j,
                    1.07414619e00 - 4.38148350e-02j,
                ],
                [
                    3.88268232e02 - 2.56252516e00j,
                    -1.88743473e-01 + 5.67293980e-01j,
                ],
                [
                    4.04077376e02 - 1.61487030e00j,
                    7.58212840e-01 + 8.53489297e-01j,
                ],
                [
                    3.94274918e02 - 2.44371900e00j,
                    -3.85495359e-01 + 3.40446011e-01j,
                ],
                [
                    3.92839281e02 - 1.83609109e00j,
                    -5.10083325e-01 - 9.02268552e-01j,
                ],
            ],
            [
                [
                    1.48650357e01 - 6.54422275e-01j,
                    5.60880526e-01 + 4.81387472e-01j,
                ],
                [
                    1.50254395e01 - 1.26717875e00j,
                    -1.57341218e-01 + 2.66772509e-01j,
                ],
                [
                    1.29949690e01 + 5.22960440e-01j,
                    -8.13317655e-01 + 6.43099241e-01j,
                ],
                [
                    1.58240635e01 - 2.31202956e-03j,
                    -3.78241756e-01 + 6.33249610e-02j,
                ],
                [
                    1.55945881e01 - 3.28907536e-01j,
                    -1.37151296e00 - 4.99179451e-01j,
                ],
            ],
            [
                [
                    3.93343001e02 + 8.29933028e-01j,
                    7.30054368e00 + 4.36169892e-01j,
                ],
                [
                    3.98730917e02 - 1.02146138e00j,
                    7.94432500e00 + 8.28471478e-01j,
                ],
                [
                    3.94964245e02 + 1.60377641e-02j,
                    7.97432796e00 + 2.02230359e-02j,
                ],
                [
                    4.03489053e02 - 5.45427738e-01j,
                    7.39863809e00 + 3.83129849e-01j,
                ],
                [
                    4.00556863e02 - 7.65334083e-01j,
                    6.96942669e00 + 1.92828490e00j,
                ],
            ],
            [
                [
                    4.30846869e02 - 9.51819995e-01j,
                    -9.63870172e-02 + 1.49935604e00j,
                ],
                [
                    4.20723860e02 - 7.56676816e-01j,
                    1.55933516e00 - 3.52749191e-01j,
                ],
                [
                    4.23614368e02 - 1.45079857e00j,
                    -1.19814025e-01 + 3.34278978e-01j,
                ],
                [
                    4.50813016e02 - 1.15075416e00j,
                    -5.40008130e-01 - 3.23734693e-01j,
                ],
                [
                    4.20960837e02 - 1.57472346e00j,
                    1.04660961e00 + 2.44574710e-01j,
                ],
            ],
        ],
        [
            [
                [
                    1.70037532e02 + 1.03960378e-01j,
                    -3.42980307e-01 + 2.59583656e-01j,
                ],
                [
                    1.59958713e02 + 1.94223049e-01j,
                    -1.52277322e-01 - 2.47124428e-01j,
                ],
                [
                    1.67878719e02 - 2.07926339e-01j,
                    1.26342705e-01 - 2.03423545e-01j,
                ],
                [
                    1.66033139e02 + 4.62792212e-01j,
                    2.17748339e-01 - 3.38881189e-02j,
                ],
                [
                    1.73258025e02 - 5.71894357e-02j,
                    -2.76404007e-01 - 1.12060503e-01j,
                ],
            ],
            [
                [
                    5.07094845e00 + 6.38058577e-01j,
                    1.25636563e-01 - 7.20912662e-01j,
                ],
                [
                    5.19299096e00 + 5.89441966e-01j,
                    -3.84883699e-01 - 4.10005401e-01j,
                ],
                [
                    4.42362242e00 + 7.80097932e-01j,
                    2.76959224e-02 - 4.91006155e-01j,
                ],
                [
                    5.20071914e00 + 4.09699057e-01j,
                    4.18600686e-01 - 1.06384541e-01j,
                ],
                [
                    5.07558517e00 - 8.65681729e-02j,
                    -2.37170508e-01 + 6.80282803e-02j,
                ],
            ],
            [
                [
                    1.39719053e02 - 6.68925341e-01j,
                    7.38478746e-01 + 4.84839527e-01j,
                ],
                [
                    1.44325650e02 - 3.70937809e-01j,
                    1.10518971e-01 + 3.14321924e-01j,
                ],
                [
                    1.50065168e02 - 8.51542701e-01j,
                    1.28999035e-01 - 3.32531625e-01j,
                ],
                [
                    1.45952858e02 - 8.46811744e-01j,
                    3.53191735e-01 + 1.81845528e-01j,
                ],
                [
                    1.45820098e02 - 6.34113841e-01j,
                    7.22193077e-01 + 9.07153254e-02j,
                ],
            ],
            [
                [
                    5.31004670e00 + 1.98795351e-01j,
                    4.44607751e-01 + 3.92759039e-03j,
                ],
                [
                    5.60219595e00 - 1.33872240e-01j,
                    9.96105541e-03 + 7.03025249e-04j,
                ],
                [
                    5.52751528e00 - 5.10820131e-02j,
                    -1.39890496e-01 + 6.83599337e-02j,
                ],
                [
                    5.50120001e00 + 2.11961283e-01j,
                    -5.43399121e-02 + 1.61210478e-01j,
                ],
                [
                    5.25283033e00 - 3.79033054e-02j,
                    -4.44428110e-01 - 1.17841744e-01j,
                ],
            ],
            [
                [
                    1.45200510e02 - 9.24200916e-02j,
                    2.41369713e00 + 6.35357714e-01j,
                ],
                [
                    1.47104264e02 - 2.31957349e-01j,
                    3.02126388e00 + 4.24061730e-01j,
                ],
                [
                    1.46290891e02 - 2.73072025e-01j,
                    2.61923949e00 + 5.90245425e-01j,
                ],
                [
                    1.48919050e02 - 5.36463682e-01j,
                    3.03665733e00 + 1.04014527e00j,
                ],
                [
                    1.47495954e02 - 2.10787968e-01j,
                    2.39693254e00 + 1.20963803e00j,
                ],
            ],
            [
                [
                    1.67766487e02 - 9.23264668e-01j,
                    -2.26440434e-02 + 1.46145035e-01j,
                ],
                [
                    1.64394346e02 - 5.55086058e-01j,
                    -2.32865794e-01 - 7.87969448e-02j,
                ],
                [
                    1.64649094e02 - 2.88744673e-01j,
                    3.16206820e-02 - 3.82978445e-02j,
                ],
                [
                    1.75729112e02 - 7.22672239e-01j,
                    9.70461301e-01 - 1.76232592e-01j,
                ],
                [
                    1.63949023e02 - 7.51418017e-01j,
                    2.27113425e-01 - 5.52177333e-02j,
                ],
            ],
        ],
        [
            [
                [
                    4.92113796e01 - 4.68499584e-02j,
                    3.02146830e-01 + 1.58314258e-01j,
                ],
                [
                    4.95735107e01 - 4.76345612e-02j,
                    1.48704571e-01 + 2.56719300e-02j,
                ],
                [
                    4.91414278e01 + 1.62326549e-02j,
                    2.71721691e-01 + 9.04583220e-02j,
                ],
                [
                    4.92786163e01 - 2.45536623e-02j,
                    2.80530816e-01 + 9.36755747e-02j,
                ],
                [
                    4.93246278e01 - 4.48216738e-03j,
                    2.11160184e-01 + 7.65497941e-02j,
                ],
            ],
            [
                [
                    1.49012561e01 + 1.80274130e-01j,
                    -7.16473787e-02 - 1.25615901e-01j,
                ],
                [
                    1.48942138e01 + 2.58565730e-01j,
                    -1.50941525e-01 + 3.15697804e-03j,
                ],
                [
                    1.48718879e01 + 2.76025901e-01j,
                    -1.17060718e-01 - 9.01112008e-02j,
                ],
                [
                    1.48542586e01 + 3.30458394e-01j,
                    -2.81904079e-02 - 1.74589062e-01j,
                ],
                [
                    1.48873594e01 + 3.99744007e-01j,
                    -1.20214583e-01 - 2.41544452e-02j,
                ],
            ],
            [
                [
                    4.79692875e01 - 3.96383578e-03j,
                    2.26203251e-01 - 3.51659136e-03j,
                ],
                [
                    4.82081247e01 - 2.18437179e-02j,
                    2.43859470e-01 - 3.29243695e-02j,
                ],
                [
                    4.80483126e01 - 4.26726399e-02j,
                    1.56465344e-01 + 7.69859300e-03j,
                ],
                [
                    4.79852147e01 - 1.79047020e-01j,
                    3.37311932e-01 + 2.54430246e-02j,
                ],
                [
                    4.81429851e01 - 4.30608373e-02j,
                    1.51884237e-01 + 5.89638131e-02j,
                ],
            ],
            [
                [
                    1.50435664e01 + 1.04125431e-02j,
                    1.58703440e-02 - 5.46142449e-02j,
                ],
                [
                    1.50017818e01 + 2.59456519e-02j,
                    -3.46928024e-02 + 2.56302718e-03j,
                ],
                [
                    1.50398965e01 + 8.07712770e-02j,
                    -7.12422040e-02 - 1.03387951e-02j,
                ],
                [
                    1.49749772e01 - 4.30480165e-02j,
                    -3.81663392e-02 - 7.92729107e-02j,
                ],
                [
                    1.50729123e01 - 6.33869363e-02j,
                    -7.70350642e-03 - 2.62162795e-02j,
                ],
            ],
            [
                [
                    4.93040790e01 + 4.45518580e-02j,
                    8.37019958e-01 - 5.84576526e-02j,
                ],
                [
                    4.91505487e01 + 3.98388832e-02j,
                    8.07782362e-01 + 1.19993712e-01j,
                ],
                [
                    4.91598354e01 + 8.36009792e-02j,
                    7.27190529e-01 + 1.71659246e-01j,
                ],
                [
                    4.90710864e01 + 1.33945480e-03j,
                    9.08133740e-01 + 9.23819902e-02j,
                ],
                [
                    4.90331456e01 - 5.68670630e-02j,
                    8.11507089e-01 + 2.02589908e-01j,
                ],
            ],
            [
                [
                    5.01995528e01 + 7.76279588e-02j,
                    4.49682371e-02 + 2.40260232e-01j,
                ],
                [
                    5.04682386e01 + 6.31752774e-02j,
                    1.65721086e-01 + 1.04570671e-01j,
                ],
                [
                    5.01548506e01 + 3.35683015e-02j,
                    1.26402215e-01 + 1.23169961e-01j,
                ],
                [
                    5.00191774e01 + 1.37974495e-01j,
                    1.32951364e-01 + 1.04147023e-01j,
                ],
                [
                    5.03309093e01 + 1.88040688e-01j,
                    1.09951724e-01 - 1.09846356e-01j,
                ],
            ],
        ],
        [
            [
                [
                    4.93193655e01 - 1.28517072e-01j,
                    2.20979318e-01 + 1.22209331e-01j,
                ],
                [
                    4.94585887e01 - 1.29979398e-01j,
                    2.06818107e-01 + 1.58109370e-01j,
                ],
                [
                    4.92445349e01 - 1.96179364e-01j,
                    2.75430973e-01 + 2.07717166e-01j,
                ],
                [
                    4.95438283e01 - 2.70065069e-01j,
                    1.86652410e-01 + 6.07133210e-02j,
                ],
                [
                    4.93841357e01 - 3.13023659e-01j,
                    2.80051264e-01 + 2.06279246e-02j,
                ],
            ],
            [
                [
                    1.48454683e01 + 2.81362389e-02j,
                    -1.28437817e-01 - 1.47524627e-01j,
                ],
                [
                    1.47438283e01 + 4.41079318e-02j,
                    -2.38463560e-01 - 1.08649213e-01j,
                ],
                [
                    1.47066155e01 + 1.97770461e-01j,
                    -1.49527384e-03 - 1.97340144e-01j,
                ],
                [
                    1.47411883e01 + 2.43274897e-01j,
                    -2.10405327e-01 - 6.08847993e-02j,
                ],
                [
                    1.46729055e01 + 1.08985918e-01j,
                    -8.21071072e-02 - 1.48128344e-01j,
                ],
            ],
            [
                [
                    4.79442531e01 - 1.74191979e-01j,
                    1.28917635e-01 - 2.09432016e-02j,
                ],
                [
                    4.81313857e01 - 1.23666029e-01j,
                    1.05089697e-01 - 1.52487483e-02j,
                ],
                [
                    4.78137974e01 - 1.73036818e-01j,
                    1.71195006e-01 - 7.44888928e-02j,
                ],
                [
                    4.81302763e01 - 2.98905069e-01j,
                    1.05453972e-01 - 8.43690965e-02j,
                ],
                [
                    4.79986887e01 - 3.12238999e-01j,
                    1.44854603e-01 - 5.13365043e-02j,
                ],
            ],
            [
                [
                    1.50380475e01 - 2.09780195e-01j,
                    1.19181241e-01 - 1.12080457e-01j,
                ],
                [
                    1.50403838e01 - 1.95451908e-01j,
                    -3.93747929e-03 - 8.53068775e-02j,
                ],
                [
                    1.50715528e01 - 1.45748265e-01j,
                    -1.11924008e-02 + 5.13011967e-02j,
                ],
                [
                    1.49631103e01 - 2.26525747e-01j,
                    -3.20137448e-02 + 3.81430136e-02j,
                ],
                [
                    1.50055688e01 - 1.63888508e-01j,
                    9.11282706e-03 + 5.86833865e-02j,
                ],
            ],
            [
                [
                    4.91702519e01 - 6.82826523e-02j,
                    7.56541237e-01 - 4.37073078e-02j,
                ],
                [
                    4.90186621e01 - 1.69861144e-02j,
                    7.22669531e-01 + 1.75969284e-02j,
                ],
                [
                    4.89955446e01 - 5.76047128e-02j,
                    6.69891737e-01 + 6.32536202e-02j,
                ],
                [
                    4.89437892e01 - 5.37727187e-02j,
                    7.08618841e-01 + 1.48004425e-01j,
                ],
                [
                    4.88838239e01 - 1.44200248e-02j,
                    7.39783061e-01 + 1.26118778e-01j,
                ],
            ],
            [
                [
                    4.99737313e01 - 5.32470192e-02j,
                    2.77436291e-01 + 1.32730740e-01j,
                ],
                [
                    5.03477469e01 + 5.48617849e-02j,
                    1.95466197e-01 + 3.77598112e-02j,
                ],
                [
                    5.00601310e01 - 3.42534434e-04j,
                    1.69560908e-01 + 1.01895857e-01j,
                ],
                [
                    5.01441067e01 + 1.10114433e-01j,
                    2.81933952e-02 + 5.32245461e-02j,
                ],
                [
                    5.01197341e01 + 9.58830407e-02j,
                    1.81852106e-01 + 2.02507112e-02j,
                ],
            ],
        ],
        [
            [
                [
                    4.97887206e01 - 9.89203338e-02j,
                    4.00858079e-01 + 1.21415356e-01j,
                ],
                [
                    4.98802319e01 - 1.00698112e-01j,
                    3.80224642e-01 + 1.36037871e-01j,
                ],
                [
                    4.99097886e01 - 2.18406884e-01j,
                    3.14735794e-01 + 5.65534692e-02j,
                ],
                [
                    4.96177051e01 - 8.20073322e-02j,
                    3.10442050e-01 + 7.65721327e-02j,
                ],
                [
                    4.97218520e01 - 3.89064147e-02j,
                    2.79385546e-01 + 1.42694385e-01j,
                ],
            ],
            [
                [
                    1.50461074e01 + 2.56717272e-01j,
                    -4.67553058e-02 + 1.30136768e-01j,
                ],
                [
                    1.50505891e01 + 3.34523486e-01j,
                    -3.23567041e-02 + 2.88017234e-02j,
                ],
                [
                    1.50665801e01 + 1.92717148e-01j,
                    -1.05137025e-01 + 4.74947972e-02j,
                ],
                [
                    1.50172777e01 + 2.83529054e-01j,
                    -1.31457787e-01 + 3.12459954e-02j,
                ],
                [
                    1.49831286e01 + 9.34106842e-02j,
                    -1.50200285e-01 - 3.52351419e-02j,
                ],
            ],
            [
                [
                    4.84588927e01 + 9.80020819e-02j,
                    3.57330608e-01 + 1.28156609e-01j,
                ],
                [
                    4.80097492e01 - 8.77482805e-02j,
                    3.93718008e-01 + 1.17006934e-01j,
                ],
                [
                    4.85769381e01 - 6.75315290e-02j,
                    4.31110763e-01 + 2.14904894e-01j,
                ],
                [
                    4.83179478e01 - 9.95108841e-02j,
                    4.18008576e-01 + 1.80989110e-01j,
                ],
                [
                    4.86026679e01 - 1.51141708e-01j,
                    5.33509780e-01 + 9.34160373e-02j,
                ],
            ],
            [
                [
                    1.49936398e01 - 1.69465790e-01j,
                    5.42990216e-02 + 2.28675719e-03j,
                ],
                [
                    1.51167688e01 - 1.53321301e-01j,
                    1.26811477e-03 - 7.40111307e-03j,
                ],
                [
                    1.51258369e01 - 1.29815763e-01j,
                    2.94352104e-02 + 1.85624678e-02j,
                ],
                [
                    1.50098407e01 - 1.88102138e-01j,
                    7.01964522e-02 + 4.64324918e-02j,
                ],
                [
                    1.51402937e01 - 1.89724549e-01j,
                    1.59151610e-01 + 1.08693072e-01j,
                ],
            ],
            [
                [
                    4.95264143e01 + 8.06133161e-02j,
                    1.00839995e00 + 2.69203640e-01j,
                ],
                [
                    4.95041360e01 + 7.16168890e-02j,
                    1.03079178e00 + 2.61896814e-01j,
                ],
                [
                    4.98101098e01 - 3.01462412e-03j,
                    1.10936731e00 + 2.65333244e-01j,
                ],
                [
                    4.99334098e01 + 1.03439381e-02j,
                    9.69528528e-01 + 2.67820153e-01j,
                ],
                [
                    5.01233015e01 + 1.05016527e-01j,
                    9.66933022e-01 + 2.53002389e-01j,
                ],
            ],
            [
                [
                    5.00166642e01 - 1.31852850e-02j,
                    2.93321964e-01 + 1.55416172e-01j,
                ],
                [
                    5.01898215e01 - 1.33801417e-01j,
                    9.18864277e-02 + 9.01758318e-02j,
                ],
                [
                    5.01111074e01 - 6.74516982e-02j,
                    2.54425069e-01 + 8.47084341e-02j,
                ],
                [
                    4.99718741e01 + 4.51283686e-02j,
                    2.10238867e-01 + 8.63284389e-02j,
                ],
                [
                    5.00468628e01 + 1.24290817e-01j,
                    2.11174193e-01 + 1.01674465e-01j,
                ],
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
                    [1.28004703 - 0.05124228j, 1.28230401 - 0.02895786j],
                    [1.28004703 - 0.05124228j, 1.28230401 - 0.02895786j],
                ]
            ],
            [
                [
                    [1.27518137 + 0.01041597j, 1.2696292 + 0.00602077j],
                    [1.27518137 + 0.01041597j, 1.2696292 + 0.00602077j],
                ]
            ],
            [
                [
                    [1.25890966 - 0.04404655j, 1.24715696 - 0.0259605j],
                    [1.25890966 - 0.04404655j, 1.24715696 - 0.0259605j],
                ]
            ],
        ],
        [
            [
                [
                    [0.72830136 - 0.32973706j, 0.76641777 - 0.17408871j],
                    [0.72830136 - 0.32973706j, 0.76641777 - 0.17408871j],
                ]
            ],
            [
                [
                    [0.73909291 - 0.292372j, 0.75744633 - 0.17389316j],
                    [0.73909291 - 0.292372j, 0.75744633 - 0.17389316j],
                ]
            ],
            [
                [
                    [0.7901212 + 0.05641375j, 0.75434651 + 0.17495435j],
                    [0.7901212 + 0.05641375j, 0.75434651 + 0.17495435j],
                ]
            ],
        ],
        [
            [
                [
                    [1.29457694 - 0.00665054j, 1.29388325 - 0.00717501j],
                    [1.29457694 - 0.00665054j, 1.29388325 - 0.00717501j],
                ]
            ],
            [
                [
                    [1.2919266 - 0.01043497j, 1.29253446 - 0.01123466j],
                    [1.2919266 - 0.01043497j, 1.29253446 - 0.01123466j],
                ]
            ],
            [
                [
                    [1.29068643 - 0.00588872j, 1.2914084 - 0.00592924j],
                    [1.29068643 - 0.00588872j, 1.2914084 - 0.00592924j],
                ]
            ],
        ],
        [
            [
                [
                    [1.28938655 + 0.09654901j, 1.28815663 + 0.05194525j],
                    [1.28938655 + 0.09654901j, 1.28815663 + 0.05194525j],
                ]
            ],
            [
                [
                    [1.28622174 - 0.11238528j, 1.28672433 - 0.00673945j],
                    [1.28622174 - 0.11238528j, 1.28672433 - 0.00673945j],
                ]
            ],
            [
                [
                    [1.28778171 - 0.05071482j, 1.28590678 + 0.01608308j],
                    [1.28778171 - 0.05071482j, 1.28590678 + 0.01608308j],
                ]
            ],
        ],
        [
            [
                [
                    [1.29599108 - 0.00483704j, 1.29601168 - 0.00516365j],
                    [1.29599108 - 0.00483704j, 1.29601168 - 0.00516365j],
                ]
            ],
            [
                [
                    [1.29325127 - 0.01399103j, 1.29326535 - 0.01417441j],
                    [1.29325127 - 0.01399103j, 1.29326535 - 0.01417441j],
                ]
            ],
            [
                [
                    [1.29543124 - 0.00243416j, 1.29545985 - 0.00216008j],
                    [1.29543124 - 0.00243416j, 1.29545985 - 0.00216008j],
                ]
            ],
        ],
    ]
)

GAIN_WEIGHT = numpy.ones(GAIN.shape)

GAIN_RESIDUAL = numpy.array(
    [
        [[[2.18231239, 0.0], [0.0, 2.37574335]]],
        [[[0.82453787, 0.0], [0.0, 0.866436]]],
        [[[0.18392438, 0.0], [0.0, 0.17862158]]],
        [[[0.19306114, 0.0], [0.0, 0.18525042]]],
        [[[0.80434434, 0.0], [0.0, 0.7954749]]],
    ]
)


# print(GAIN.shape)
print(GAIN_WEIGHT.shape)
print(GAIN_RESIDUAL.shape)
print("=" * 30)


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

ACTUAL_SOURCE = numpy.array([[5.14618, -1.112], [0, 0]])


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
        if columnname == "SOURCE_OFFSET":
            return numpy.dstack((DISH_COORD_AZ, DISH_COORD_EL))

        if columnname == "DIRECTION":
            return numpy.dstack((ACTUAL_POINTING_AZ, ACTUAL_POINTING_EL))

        if columnname == "TIME":
            return POINTING_TIMESTAMPS

        if columnname == "TARGET":
            return numpy.dstack((ACTUAL_POINTING_AZ, ACTUAL_POINTING_EL))


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
