# -*- coding: utf-8 -*-

from __future__ import division

import itertools
import math
import numpy as np
from pandas import DataFrame

__author__ = "kissg"
__date__ = "2017-04-11"

PITCH_PROBABILITY = None


def cal_length_similarity(l1, l2):
    distance = abs(l1 - l2)
    return 1.0 - distance * 0.3 if distance < 4 else 0.0


def cal_duration_similarity(d1, d2):
    result = 1.0
    cor_pair = zip(d1, d2)
    for i1, i2 in cor_pair:
        if i1 == i2:
            continue
        elif i1 / i2 in (2.0, 0.5):
            result -= 0.1
        elif i1 / i2 in (4.0, 0.25):
            result -= 0.2
        else:
            result -= 0.3
    return result if result > 0.0 else 0.0


def cal_pitch_similarity(p1, p2):
    result = 1.0
    cor_pair = zip(p1, p2)
    for i1, i2 in cor_pair:
        result -= 0.25 if i1 != i2 else 0
    return result if result > 0.0 else 0.0


def cal_octave_similarity(o1, o2):
    result = 1.0
    cor_pair = zip(o1, o2)
    for i1, i2 in cor_pair:
        if i1 == i2:
            continue
        elif abs(i1 - i2) == 1:
            result -= 0.1
        elif abs(i1 - i2) == 2:
            result -= 0.2
        else:
            result -= 0.3
    return result if result > 0.0 else 0.0


def cal_change_similarity(c1, c2):
    result = 1.0
    cor_pair = zip(c1, c2)
    for i1, i2 in cor_pair:
        if i1 == i2:
            continue
        elif (i1 < 0) == (i2 < 0):
            result -= 0.1
        else:
            result -= 0.3
    return result if result > 0.0 else 0.0


def cal_bar_similarity(bars):
    lengths, durations, pitchs, octaves, duration_change, pitch_change, \
    octave_change = [], [], [], [], [], [], []

    for bar in bars:
        lengths.append(len(bar))
        ds, ps = zip(*[math.modf(note) for note in bar])
        durations.append([int(round(d * 100)) for d in ds])
        pitchs.append([int(p) for p in ps])
        octaves.append([p // 12 for p in pitchs[-1]])
        duration_change.append(
            [n / p for p, n in zip(durations[-1][:-1], durations[-1][1:])])
        pitch_change.append(
            [n - p for p, n in zip(pitchs[-1][:-1], pitchs[-1][1:])])
        octave_change.append(
            [n - p for p, n in zip(octaves[-1][:-1], octaves[-1][1:])])

    features = zip(lengths, durations, pitchs, octaves, duration_change,
                   pitch_change, octave_change)

    distances = {}
    for p, n in itertools.permutations(features, 2):
        if p == n:
            continue
        index_p, index_n = features.index(p), features.index(n)
        s_length = cal_length_similarity(p[0], n[0])
        s_duration = cal_duration_similarity(p[1], n[1])
        s_pitch = cal_pitch_similarity(p[2], n[2])
        s_octave = cal_octave_similarity(p[3], n[3])
        s_duration_change = cal_change_similarity(p[4], n[4])
        s_pitch_change = cal_change_similarity(p[5], n[5])
        s_octave_change = cal_change_similarity(p[6], n[6])
        if index_p in distances.keys():
            distances[index_p].update({index_n: np.mean([s_length, s_duration,
                                                         s_pitch, s_octave,
                                                         s_duration_change,
                                                         s_pitch_change,
                                                         s_octave_change])})
        else:
            distances[index_p] = {index_n: np.mean([s_length, s_duration,
                                                    s_pitch, s_octave,
                                                    s_duration_change,
                                                    s_pitch_change,
                                                    s_octave_change])}
    distances_df = DataFrame(distances)
    return distances_df
