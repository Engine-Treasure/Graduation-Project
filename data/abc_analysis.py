# -*- coding: utf-8 -*-
from __future__ import division

import os
import json
import glob
from copy import deepcopy
from fractions import Fraction
from collections import Counter, OrderedDict

import numpy as np
import joblib

import src.abcparse as abcparse


# if not os.path.exists("ABCs"):
#     os.makedirs("ABCs")

# with open("session_data_clean.txt") as f:
#     abcs = f.read().split("\n\n")

# for i, abc in enumerate(abcs):
#     with open(os.path.join("ABCs", str(i) + ".abc"), "w") as f:
#         f.write(abc + "\n\n")


def get_N_grams(_input, n):
    output = dict()  # store n-tuple
    # str or float
    if isinstance(_input[0], float):
        _input = [
            str(Fraction(1 / ele).limit_denominator(32)) for ele in _input
            ]
    for i in range(len(_input) - n + 1):
        n_gram = ' '.join(_input[i: i + n])  # 相邻的单词构成一个n元组
        if n_gram in output:  # 统计n元组的词频
            output[n_gram] += 1
        else:
            output[n_gram] = 1
    return output


def compute_statistics(abc_file):
    """

    :param abc_file: str - path to a abc file
    :return:
    """
    try:
        key, meter, notes = abcparse.parse_abc(abc_file)
        km = key + "_" + meter

        names, durations = zip(*notes)
        names = [n.rstrip("*") for n in names]

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
                "names_2": names_2,
                "names_3": names_3,
                "names_4": names_4,
                "duration_2": duration_2,
                "duration_3": duration_3,
                "duration_4": duration_4,

            }
        }
    except Exception as e:
        pass


def concat_statistics(a, b):
    # d = deepcopy(a)  # The previous reduce result is a.

    for km, nd in b.iteritems():
        if km in a.keys():
            for k, v in nd.iteritems():
                a[km][k].update(v)  # update Counter

        else:
            a[km] = nd  # add new key and meter combination
    return a


def classify_key_meter(statistics):
    on_key = {}
    on_meter = {}

    for km, nd in statistics.iteritems():
        key, meter = km.split("_")

        if key in on_key.keys():
            for k, v in nd.iteritems():
                on_key[key][k].update(v)
        else:
            on_key[key] = nd

        if meter in on_meter.keys():
            for k, v in nd.iteritems():
                on_meter[meter][k].update(v)
        else:
            on_meter[meter] = nd

    return on_key, on_meter


statistics = joblib.Parallel(n_jobs=1, verbose=0)(  # n_jobs > 1, has problem
    joblib.delayed(compute_statistics)(abc_file)
    for abc_file in glob.glob(os.path.join("ABCs", "999*.abc")))

# statistics = (compute_statistics(abc_file)
#               for abc_file in glob.glob(os.path.join("ABCs", "999*.abc")))
statistics = (s for s in statistics if s is not None)  # eliminate None values

initial_d = {"C_4/4": {"name": Counter({}), "duration": Counter({})}}
statistics = reduce(concat_statistics, statistics, initial_d)
print(statistics.values())

keys, meters = zip(*map(lambda s: s.split("_"), statistics.keys()))

statistics_on_key, statistics_on_meter = classify_key_meter(statistics)
