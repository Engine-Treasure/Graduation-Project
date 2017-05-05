# -*- coding: utf-8 -*-

from __future__ import division

import itertools
import math
import numpy as np
from pandas import DataFrame

from evaluate import grade_chord, grade_interval, grade_duration, grade_markov

__author__ = "kissg"
__date__ = "2017-04-11"

PITCH_PROBABILITY = None

# s_length - 长度相似度
# s_duration - 时值相似性
# s_pitch - 音高相似性
# s_octave - 八度相似性
# s_duration_change - 时值变化相似性
# s_pitch_change - 音高变化相似性
# s_octave_change - 八度变化相似性
# W = (1.0, 0.7, 0.8, 0.2, 0.7, 0.8, 0.2)
W = (1.0, 0.7, 0.8, 0.2, 0.7, 0.8, 0.2, 1.0)


def cal_similarity_length(l1, l2):
    distance = abs(l1 - l2)
    # return 1.0 - distance * 0.3 if distance < 4 else 0.0
    return 1.0 if not distance else 0.0


def cal_similarity_general(g1, g2):
    result = 1.0
    deduction = 1.0 / len(max(g1, g2))  # 长度相关的扣分标准
    cor_pair = itertools.izip_longest(g1, g2, fillvalue=666)
    for i1, i2 in cor_pair:
        result -= deduction if i1 != i2 else 0
    return result


# def cal_duration_similarity(d1, d2):
#     result = 1.0
#     # cor_pair = zip(d1, d2)
#     cor_pair = itertools.izip_longest(d1, d2, fillvalue=666)
#     for i1, i2 in cor_pair:
#         if i1 == i2:
#             continue
#         elif i1 / i2 in (2.0, 0.5):
#             result -= 0.1
#         elif i1 / i2 in (4.0, 0.25):
#             result -= 0.2
#         else:
#             result -= 0.3
#     return result if result > 0.0 else 0.0
#
#
# def cal_pitch_similarity(p1, p2):
#     result = 1.0
#     # cor_pair = zip(p1, p2)
#     cor_pair = itertools.izip_longest(p1, p2, fillvalue=666)
#     for i1, i2 in cor_pair:
#         result -= 0.25 if i1 != i2 else 0
#     return result if result > 0.0 else 0.0
#
#
# def cal_octave_similarity(o1, o2):
#     result = 1.0
#     # cor_pair = zip(o1, o2)
#     cor_pair = itertools.izip_longest(o1, o2, fillvalue=666)
#     for i1, i2 in cor_pair:
#         if i1 == i2:
#             continue
#         elif abs(i1 - i2) == 1:
#             result -= 0.1
#         elif abs(i1 - i2) == 2:
#             result -= 0.2
#         else:
#             result -= 0.3
#     return result if result > 0.0 else 0.0


def cal_similarity_change(c1, c2):
    result = 1.0
    deduction = 1.0 / len(max(c1, c2))  # 长度相关的扣分标准
    cor_pair = itertools.izip_longest(c1, c2, fillvalue=666)
    for i1, i2 in cor_pair:
        if i1 == i2:
            continue
        elif (i1 < 0) == (i2 < 0):  # same sign
            result -= deduction / 2.0
        else:
            result -= deduction
    return result








def cal_bar_similarity(bars):
    lengths, durations, pitchs, octaves, duration_change, pitch_change, \
        octave_change = [], [], [], [], [], [], []

    # 提取特征: 长度, 时值, 音高, 八度, 时值变化, 音高变化, 八度变化
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

    # 二级字典
    distances = {}
    for p, n in itertools.permutations(features, 2):
        # 索引用于构建字典的 key
        index_p, index_n = features.index(p), features.index(n)

        s_length = cal_similarity_length(p[0], n[0])
        s_duration = cal_similarity_general(p[1], n[1])
        s_pitch = cal_similarity_general(p[2], n[2])
        s_octave = cal_similarity_general(p[3], n[3])
        s_duration_change = cal_similarity_change(p[4], n[4])
        s_pitch_change = cal_similarity_change(p[5], n[5])
        s_octave_change = cal_similarity_change(p[6], n[6])

        c_chord = grade_chord([p[2][-1] % 12, n[2][0] % 12])
        c_duration = grade_duration([p[1][-1], n[1][0]])
        c_pitch = grade_interval([p[2][-1], n[2][0]])
        c_markov = grade_markov([p[2][-1], n[2][0]])
        s_convergence = np.mean([c_chord, c_pitch, c_duration, c_markov])

        if index_p in distances.keys():
            distances[index_p].update({
                index_n: np.average([
                    s_length, s_duration, s_pitch, s_octave, s_duration_change,
                    s_pitch_change, s_octave_change, s_convergence
                ], weights=W)
            })
        else:
            distances[index_p] = {
                index_n: np.average([
                    s_length, s_duration, s_pitch, s_octave, s_duration_change,
                    s_pitch_change, s_octave_change, s_convergence
                ], weights=W)
            }
    distances_df = DataFrame(distances)
    return distances_df
