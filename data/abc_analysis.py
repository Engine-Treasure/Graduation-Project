# -*- coding: utf-8 -*-
from __future__ import division

import glob
import json
import os
from collections import Counter
from copy import deepcopy
from fractions import Fraction

from send_email import send_email

try:
    import abcparse
except ImportError:
    import gamcs.abcparse as abcparse

if not os.path.exists("ABCs"):
    os.makedirs("ABCs")

with open("sessions_data_clean.txt") as f:
    abcs = f.read().split("\n\n")

n_subdirs = len(abcs) // 5000
for i in range(n_subdirs + 1):
    if not os.path.exists(os.path.join("ABCs", str(i))):
        os.makedirs(os.path.join("ABCs", str(i)))

for i, abc in enumerate(abcs):
    subdir = i // 5000

    with open(os.path.join("ABCs", str(subdir), str(i) + ".abc"), "w") as f:
        f.write(abc + "\n\n")


def get_N_grams(_input, n):
    output = dict()  # store n-tuple
    # str or float
    # if isinstance(_input[0], float):
    #     _input = [
    #         str(Fraction(1 / ele).limit_denominator(32)) for ele in _input
    #         ]
    for i in range(len(_input) - n + 1):
        n_gram = ' '.join(_input[i: i + n])  # 相邻的单词构成一个n元组
        if n_gram in output:  # 统计n元组的词频
            output[n_gram] += 1
        else:
            output[n_gram] = 1
    return output


def compute_statistics(abc_file):
    """
    Compute statistics: note, names(pitch), duration
    :param abc_file: str - path to a abc file
    :return:
    """
    try:
        key, meter, notes = abcparse.parse_abc(abc_file)
        km = key + "_" + meter

        names, durations = zip(*notes)
        names = [n.rstrip("*") for n in names]  # strip louder symbol `*`

        # convert duration to fraction form
        durations = [  # denominator - 分母
                       str(Fraction(1 / ele).limit_denominator(32)) for ele in
                       durations]

        notes = (
            name + "_" + duration for name, duration in zip(names, durations))

        names_2 = get_N_grams(names, 2)
        names_3 = get_N_grams(names, 3)
        names_4 = get_N_grams(names, 4)
        duration_2 = get_N_grams(durations, 2)
        duration_3 = get_N_grams(durations, 3)
        duration_4 = get_N_grams(durations, 4)

        return {
            km: {
                "name": Counter(names),
                "duration": Counter(durations),
                "note": Counter(notes),
                "name_2": Counter(names_2),
                "name_3": Counter(names_3),
                "name_4": Counter(names_4),
                "duration_2": Counter(duration_2),
                "duration_3": Counter(duration_3),
                "duration_4": Counter(duration_4),
            }
        }
    except Exception as e:
        pass


def concat_statistics(a, b):
    for km, nd in b.iteritems():
        if km in a.keys():
            for k, v in nd.iteritems():
                a[km][k].update(v)  # update Counter

        else:
            a[km] = nd  # add new key and meter combination
    return a


def classify(statistics):
    flat = {}
    on_key = {}
    on_meter = {}

    for km, nd in statistics.iteritems():
        key, meter = km.split("_")

        for k, v in nd.iteritems():
            if k in flat.keys():
                flat[k].update(v)
            else:
                flat[k] = deepcopy(v)  # !!! 如果不是深度复制, 会修改 statistics

        if key in on_key.keys():
            for k, v in nd.iteritems():
                on_key[key][k].update(v)
        else:
            on_key[key] = deepcopy(nd)

        if meter in on_meter.keys():
            for k, v in nd.iteritems():
                on_meter[meter][k].update(v)
        else:
            on_meter[meter] = deepcopy(nd)

    return flat, on_key, on_meter


# import joblib
# statistics = joblib.Parallel(n_jobs=1, verbose=0)(  # n_jobs > 1, has problem
#     joblib.delayed(compute_statistics)(abc_file)
#     for abc_file in glob.glob(os.path.join("ABCs", "999*.abc")))


subdirs = os.listdir("ABCs")

for sd in subdirs:
    statistics = (compute_statistics(abc_file)
                  for abc_file in
                  glob.iglob(os.path.join("ABCs", sd, "*.abc")))

    statistics = (s for s in statistics if
                  s is not None)  # eliminate None value

    statistics = reduce(concat_statistics, statistics)

    with open("abc_result.txt" + subdir, "w") as f:
        f.write(json.dumps(statistics))


# statistics_flat, statistics_key, statistics_meter = classify(statistics)
#
#
# with open("abc_result_flat.txt", "w") as f:
#     f.write(json.dumps(statistics_flat))
#
# with open("abc_result_key.txt", "w") as f:
#     f.write(json.dumps(statistics_key))
#
# with open("abc_result_meter.txt", "w") as f:
#     f.write(json.dumps(statistics_meter))

send_email()
