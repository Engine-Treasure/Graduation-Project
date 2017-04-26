# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-22"

import os

import pandas as pd

name2int = {
    "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
    "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11
}

# pitch_frequencies from some abc file
old_pitch_frequencies = {
    9: 0.000103035426, 10: 6.65895269e-05, 11: 0.000144871778,
    12: 0.000406509887, 13: 0.0002279813, 14: 0.000801729322, 15: 0.00102075335,
    16: 0.00265840517, 17: 0.00251828021, 18: 0.00150449958, 19: 0.00452757828,
    20: 0.00193670128, 21: 0.0056636766, 22: 0.00330898726, 23: 0.0173566688,
    24: 0.0281308971, 25: 0.00740388112, 26: 0.0257655074, 27: 0.00622291599,
    28: 0.0231936176, 29: 0.00877565755, 30: 0.0536855868, 31: 0.0131455181,
    32: 0.0141893351, 33: 0.0190733269, 34: 0.0129340568, 35: 0.0114861436,
    36: 0.0150094617, 37: 0.00848789854, 38: 0.0197091054, 39: 0.0204910161,
    40: 0.020698562, 41: 0.0150143426, 42: 0.0238417593, 43: 0.0283664948,
    44: 0.0158714247, 45: 0.0350884702, 46: 0.0159338037, 47: 0.0338627187,
    48: 0.0344641163, 49: 0.0214787295, 50: 0.0437150455, 51: 0.0196410945,
    52: 0.0454560546, 53: 0.0259801868, 54: 0.0236267043, 55: 0.0343481009,
    56: 0.0151884999, 57: 0.0401343365, 58: 0.0193568755, 59: 0.0198895917,
    60: 0.0191187033, 61: 0.0100959431, 62: 0.018771837, 63: 0.00784150008,
    64: 0.0143553664, 65: 0.00894858114, 66: 0.00653475772, 67: 0.00950693553,
    68: 0.00455276055, 69: 0.00823229452, 70: 0.00537559577, 71: 0.00432022016,
    72: 0.0040672175, 73: 0.00222480892, 74: 0.00355263037, 75: 0.00145890868,
    76: 0.00201586853, 77: 0.00135404962, 78: 0.00081599659, 79: 0.00119190694,
    80: 0.000493052135, 81: 0.000769279331, 82: 0.000424075791,
    83: 0.000371190351, 84: 0.000402567615, 85: 0.000186359493,
    86: 0.000244796295, 87: 0.000165950863, 88: 0.00018979222,
    89: 0.000124650874, 90: 8.47722491e-05, 91: 0.000120145421,
    92: 4.27749881e-05, 93: 4.16218066e-05, 94: 3.85108983e-05,
    95: 1.70027225e-05, 96: 4.04686251e-05
}

# pitch_frequencies from some abc file
# represents as list
old_pitch_frequencies_ls = [
    1.03035426e-04, 6.65895269e-05, 1.44871778e-04, 4.06509887e-04,
    2.27981300e-04, 8.01729322e-04, 1.02075335e-03, 2.65840517e-03,
    2.51828021e-03, 1.50449958e-03, 4.52757828e-03, 1.93670128e-03,
    5.66367660e-03, 3.30898726e-03, 1.73566688e-02, 2.81308971e-02,
    7.40388112e-03, 2.57655074e-02, 6.22291599e-03, 2.31936176e-02,
    8.77565755e-03, 5.36855868e-02, 1.31455181e-02, 1.41893351e-0,
    1.90733269e-02, 1.29340568e-02, 1.14861436e-02, 1.50094617e-02,
    8.48789854e-03, 1.97091054e-02, 2.04910161e-02, 2.06985620e-02,
    1.50143426e-02, 2.38417593e-02, 2.83664948e-02, 1.58714247e-02,
    3.50884702e-02, 1.59338037e-02, 3.38627187e-02, 3.44641163e-02,
    2.14787295e-02, 4.37150455e-02, 1.96410945e-02, 4.54560546e-02,
    2.59801868e-02, 2.36267043e-02, 3.43481009e-02, 1.51884999e-02,
    4.01343365e-02, 1.93568755e-02, 1.98895917e-02, 1.91187033e-02,
    1.00959431e-02, 1.87718370e-02, 7.84150008e-03, 1.43553664e-02,
    8.94858114e-03, 6.53475772e-03, 9.50693553e-03, 4.55276055e-03,
    8.23229452e-03, 5.37559577e-03, 4.32022016e-03, 4.06721750e-03,
    2.22480892e-03, 3.55263037e-03, 1.45890868e-03, 2.01586853e-03,
    1.35404962e-03, 8.15996590e-04, 1.19190694e-03, 4.93052135e-04,
    7.69279331e-04, 4.24075791e-04, 3.71190351e-04, 4.02567615e-04,
    1.86359493e-04, 2.44796295e-04, 1.65950863e-04, 1.89792220e-04,
    1.24650874e-04, 8.47722491e-05, 1.20145421e-04, 4.27749881e-05,
    4.16218066e-05, 3.85108983e-05, 1.70027225e-05, 4.04686251e-05
]

# result from 170000+ midi files, piano keys only
new_pitch_frequencies = {
    "9": 7.5310128456966375e-06, "10": 8.77660583494478e-06,
    "11": 2.035671664746403e-05, "12": 2.1665657358223316e-05,
    "13": 9.815950428575253e-06, "14": 2.217096592748661e-05,
    "15": 1.8883513821623533e-05, "16": 3.218948174461493e-05,
    "17": 2.703548165841194e-05, "18": 1.7207009005817044e-05,
    "19": 5.00667980361894e-05, "20": 4.379021739669595e-05,
    "21": 0.00011223374748241975, "22": 0.00011262193642702872,
    "23": 0.00022965243231038514, "24": 0.000658444320002347,
    "25": 0.00048581662267459594, "26": 0.0014215007726676278,
    "27": 0.001629476498598596, "28": 0.004457371822157683,
    "29": 0.0033981861328687903, "30": 0.002591401337325499,
    "31": 0.0064411410781469, "32": 0.00287655300309236,
    "33": 0.008022415853486821, "34": 0.004434676396024197,
    "35": 0.026906108669253692, "36": 0.03614207756033087,
    "37": 0.008705672592083387, "38": 0.02989573735524344,
    "39": 0.008633081259441509, "40": 0.023428974333549523,
    "41": 0.009283279326626212, "42": 0.07348693683579094,
    "43": 0.012560779210799324, "44": 0.01579042504758066,
    "45": 0.012957965005065703, "46": 0.016769005917456514,
    "47": 0.00879498625000138, "48": 0.01219210578402426,
    "49": 0.007705861396284343, "50": 0.014777814665630712,
    "51": 0.01760642670236457, "52": 0.015605654475960917,
    "53": 0.01411416257363902, "54": 0.029073391118250795,
    "55": 0.02459921005185027, "56": 0.013546412302602479,
    "57": 0.02965258375563564, "58": 0.015482991189072958,
    "59": 0.02717668446626169, "60": 0.032117201994370716,
    "61": 0.0182469001576959, "62": 0.03913671218952282,
    "63": 0.02001390234989095, "64": 0.036960412266028746,
    "65": 0.02471120145746784, "66": 0.019501734548270543,
    "67": 0.031403979573695145, "68": 0.013612699063751172,
    "69": 0.038680936382271346, "70": 0.024124600083071844,
    "71": 0.017703797306537088, "72": 0.01898563918791645,
    "73": 0.010048587569810792, "74": 0.018060824328372468,
    "75": 0.008184033569495652, "76": 0.014311906169343112,
    "77": 0.009259632948068646, "78": 0.006504519736917384,
    "79": 0.00949359818165168, "80": 0.005338341219198999,
    "81": 0.00836368770770125, "82": 0.009504340040056297,
    "83": 0.004375394714312376, "84": 0.004028455448826938,
    "85": 0.002436432185669685, "86": 0.0033410840547377996,
    "87": 0.0015492628145358195, "88": 0.0019816544733327226,
    "89": 0.0013280105847383768, "90": 0.0008381765379577139,
    "91": 0.001198948441376381, "92": 0.0005402551500964671,
    "93": 0.0007892080126281885, "94": 0.0004144045888948035,
    "95": 0.00040952386793279396, "96": 0.0004606918850812991
}

new_pitch_frequencies_ls = [
    7.5310128456966375e-06, 8.77660583494478e-06, 2.035671664746403e-05,
    2.1665657358223316e-05, 9.815950428575253e-06, 2.217096592748661e-05,
    1.8883513821623533e-05, 3.218948174461493e-05, 2.703548165841194e-05,
    1.7207009005817044e-05, 5.00667980361894e-05, 4.379021739669595e-05,
    0.00011223374748241975, 0.00011262193642702872, 0.00022965243231038514,
    0.000658444320002347, 0.00048581662267459594, 0.0014215007726676278,
    0.001629476498598596, 0.004457371822157683, 0.0033981861328687903,
    0.002591401337325499, 0.0064411410781469, 0.00287655300309236,
    0.008022415853486821, 0.004434676396024197, 0.026906108669253692,
    0.03614207756033087, 0.008705672592083387, 0.02989573735524344,
    0.008633081259441509, 0.023428974333549523, 0.009283279326626212,
    0.07348693683579094, 0.012560779210799324, 0.01579042504758066,
    0.012957965005065703, 0.016769005917456514, 0.00879498625000138,
    0.01219210578402426, 0.007705861396284343, 0.014777814665630712,
    0.01760642670236457, 0.015605654475960917, 0.01411416257363902,
    .029073391118250795, 0.02459921005185027, 0.013546412302602479,
    0.02965258375563564, 0.015482991189072958, 0.02717668446626169,
    0.032117201994370716, 0.0182469001576959, 0.03913671218952282,
    0.02001390234989095, 0.036960412266028746, 0.02471120145746784,
    0.019501734548270543, 0.031403979573695145, 0.013612699063751172,
    0.038680936382271346, 0.024124600083071844, 0.017703797306537088,
    0.01898563918791645, 0.010048587569810792, 0.018060824328372468,
    0.008184033569495652, 0.014311906169343112, 0.009259632948068646,
    0.006504519736917384, 0.00949359818165168, 0.005338341219198999,
    0.00836368770770125, 0.009504340040056297, 0.004375394714312376,
    0.004028455448826938, 0.002436432185669685, 0.0033410840547377996,
    0.0015492628145358195, 0.0019816544733327226, 0.0013280105847383768,
    0.0008381765379577139, 0.001198948441376381, 0.0005402551500964671,
    0.0007892080126281885, 0.0004144045888948035, 0.00040952386793279396,
    0.0004606918850812991
]

pitch_frequencies_cmaj = [
    0.00015304295602176413, 0, 0.00021518429155860218, 0.0006038066437319657, 0,
    0.0011908430928232855, 0, 0.003948643697754406, 0.0037405100594188737, 0,
    0.006725007024197042, 0, 0.00841250279117878, 0, 0.025780607728478996,
    0.041784033073518544, 0, 0.03827061787366841, 0, 0.03445047918123243,
    0.013034862130688064, 0, 0.01952560421753975, 0, 0.028330433941675857, 0,
    0.01706086380265432, 0.022294199927541943, 0, 0.02927478313100306, 0,
    0.03074446563534137, 0.02230144973853459, 0, 0.042133976484631616, 0,
    0.05211841606487444, 0, 0.050297754568234335, 0.0511910363259901, 0,
    0.06493183990859532, 0, 0.06751783571090111, 0.03858949043283052, 0,
    0.05101871365553259, 0, 0.05961325860808479, 0, 0.029542867206022377,
    0.028397833462978618, 0, 0.027882618007894926, 0, 0.0213226440062616,
    0.013291712986814924, 0, 0.014121060810866516, 0, 0.012227781619329357, 0,
    0.006417009077549879, 0.0060412133297090415, 0, 0.005276874902011796, 0,
    0.002994256352008952, 0.002011228220136116, 0, 0.0017703907139710907, 0,
    0.0011426437235547038, 0, 0.0005513450156822392, 0.0005979510173348677, 0,
    0.0003636064804543614, 0, 0.0002819065588056382, 0.00018514931192361415, 0,
    0.00017845716853074725, 0, 6.182266201364736e-05, 0, 2.5254876044456398e-05,
    6.0109791863631066e-05
]

duration_frequencies = [
    0.00016389949682854473, 0.013882287381377739, 0.12196581056496157,
    0.7440791306770688, 0.11961385278547194, 0.0002950190942913805]

duration_frequencies_hard_code = [
    0.025, 0.15, 0.4, 0.275, 0.125, 0.025
]

columns = [
    'C-18', 'C#-11', 'C-11', 'B-10', 'A#-10', 'F-11', 'E-11', 'D#-11', 'D-11',
    'G-11', 'F#-11', 'C-2', 'C#-2', 'D-2', 'D#-2', 'G#-1', 'A-1', 'A#-1', 'B-1',
    'E-13', 'E-2', 'F-2', 'C-0', 'E-0', 'G#-0', 'D#-7', 'C-10', 'C#-10', 'D-10',
    'D#-10', 'E-10', 'F-10', 'F#-10', 'G-10', 'G#-10', 'A-10', 'B-4', 'A#-4',
    'G-4', 'F#-4', 'A-4', 'G#-4', 'D#-4', 'D-4', 'F-4', 'E-4', 'G#-16', 'D#-16',
    'C#-16', 'C-16', 'G-9', 'F#-9', 'E-7', 'G#-9', 'D#-9', 'D-9', 'F-9', 'E-9',
    'A#-6', 'B-6', 'G#-6', 'A-6', 'B-9', 'A#-9', 'C-7', 'C#-7', 'D#-0', 'G-0',
    'G-20', 'C-9', 'C#-9', 'F#-8', 'G-8', 'E-8', 'F-8', 'A#-8', 'B-8', 'G#-8',
    'A-8', 'D#-3', 'D-3', 'A-2', 'G#-2', 'G-2', 'F#-2', 'C#-3', 'C-3', 'B-2',
    'A#-2', 'D-7', 'C-5', 'C#-5', 'D-5', 'D#-5', 'E-5', 'F-5', 'F#-5', 'G-5',
    'G#-5', 'A-5', 'C#-21', 'D-21', 'D#-21', 'C#-15', 'C#-12', 'D-15', 'D#-15',
    'D-0', 'G-15', 'E-15', 'F#-0', 'D#-8', 'D-8', 'C#-19', 'G-7', 'F#-7', 'A-7',
    'G#-7', 'B-7', 'A#-7', 'C#-8', 'C-8', 'B-0', 'A#-0', 'C#-1', 'C-1', 'D#-1',
    'D-1', 'F-1', 'E-1', 'G-1', 'F#-1', 'B-11', 'A-9', 'F-7', 'G-12', 'F#-12',
    'A-12', 'G#-12', 'B-12', 'A#-12', 'E-19', 'C-4', 'C#-4', 'A#-3', 'B-3',
    'G#-3', 'A-3', 'F#-3', 'G-3', 'E-3', 'F-3', 'C#-0', 'F-0', 'A-0', 'D-12',
    'D#-12', 'C-12', 'A#-16', 'A#-11', 'C-17', 'G#-11', 'A-11', 'E-12', 'F-12',
    'F-6', 'E-6', 'D#-6', 'D-6', 'C#-6', 'C-6', 'B-5', 'A#-5', 'G-6', 'F#-6'
]

markov_table = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                        "statics/markov_table.csv"),
                           index_col=[0])
markov_table.columns = markov_table.columns.astype(int)

# with open("statics/pitch_markov_table_rank.txt") as f:
#     markov_table_rank = json.load(f)
