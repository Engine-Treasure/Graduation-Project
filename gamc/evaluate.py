# -*- coding: utf-8 -*-

"""
- grade_chord - 对相邻音符的协和度打分
- grade_interval - 对相邻音符的音程打分
- grade_duration - 对相邻音符的时值差打分
- grade_markov - 基于以马尔可夫表表示的作曲经验打分
- grade_in - 对音符所在区间打分
- grade_length - 对小节长度打分, 过长的小节, 音符太短促, 刺耳
- grade_pitch_change - 对小节变化的打分: 是否出现连续相同的音高
- grade_duration_change - 对小节变化的打分: 是否出现连续相同的时值
- grade_pitch_diversity - 对小节多样性的打分: 小节包含的音高数
- grade_duration_diversity - 对小节多样性的打分: 小节包含的时值数
"""

from __future__ import division

import math
import numpy as np

import util
from statistics import markov_table

__author__ = "kissg"
__date__ = "2017-03-30"

int2name = {
    0: "C", 1: "C#", 2: "D", 3: "D#", 4: "E", 5: "F",
    6: "F#", 7: "G", 8: "G#", 9: "A", 10: "A#", 11: "B"
}


chord_score = {
    0: 0.2,  # 纯一度, 纯八度, 太协和, 也太空洞, 比刺激好一点
    3: 1.0,  # 小三度
    4: 0.9,  # 大三度
    5: 0.6,  # 纯四度
    7: 0.5,  # 纯五度
    8: 0.7,  # 小六度
    9: 0.8   # 大六度
}


def grade_chord(names):
    """
    对协和打分 
    纯一度或纯八度, 为极协和音程,
    纯四度或纯五度, 协和音程,
    大三度, 小三度, 大六度, 小六度, 不完全协和音程
    以上属于相对协和音程
    大二度, 小二度, 大七度, 小七度, 不协和音程
    其他为极不协和音程
    """
    result = 0.0
    score = 1.0 / (len(names) - 1)

    punishment = 0
    for p, n in zip(names[:-1], names[1:]):
        x = n - p  # 后者减前者
        x = 12 - x * -1 if x < 0 else x  # 统计半音

        # todo: 更好的评分标准
        if x in [0, 3, 4, 5, 7, 8, 9]:
            result += chord_score[x] * score
        else:
            punishment += 1

    if punishment * 2 > len(names):  # 不协和音程占据半数以上
        return 0.0
    else:
        return result / (punishment + 1.0)


def grade_interval(pitchs):
    """
    音程超过一个八度, 变化剧烈, 不和谐
    """
    result = 0.0
    score = 1.0 / (len(pitchs) - 1)

    punishment = 0
    for p, n in zip(pitchs[:-1], pitchs[1:]):
        diff = abs(n - p)  # 音程, 后一个音符减前一个音符
        if not diff:  # 音程为 0, 同一个音
            result += 0.5 * score
        elif diff < 8:
            result += score
        elif diff >= 16:  # 音程超过 16 度的, 0 分
            return 0.0
        else:
            punishment += 1  # 音程在 [8, 16) 间的, 不得分, 但依据其出现次数评分

    if punishment < 3:
        return result / (punishment + 1.0)  # 两次音程在 [8, 16) 间, 评分减半
    else:  # 两次以上, 就以 0 分处理
        return 0.0


# def grade_octave(octave_diffrence):
#     """
#     不同八度, 音的差别较大, 八度相差越大, 音变化越剧烈, 刺耳
#     """
#     if not octave_diffrence:  # 同一个八度
#         return 1.0
#     elif abs(octave_diffrence) == 1:  # 差一个八度
#         return 0.8
#     elif abs(octave_diffrence) == 2:
#         return 0.5
#     elif abs(octave_diffrence) == 3:
#         return 0.25
#     else:
#         return 0.0


def grade_duration(durations):
    """
    对时值打分 - 时值变化越剧烈, 越不舒服
    """
    result = 0.0
    score = 1.0 / (len(durations) - 1)

    punishment = 0
    for p, n in zip(durations[:-1], durations[1:]):
        ratio = n / p
        if ratio == 1.0:
            result += 0.5 * score
        elif ratio in (0.5, 2.0):
            result += score
        elif ratio in (0.25, 4.0):
            result += 0.25 * score  # 时值差等于 4 倍, 已经比较刺耳了
        else:
            punishment += 1  # 时值超过 4 倍, 太突兀, 听着极不舒服

    if punishment < 3:
        return result / (punishment + 1.0)  # 两次音程在 [8, 16) 间, 评分减半
    else:  # 两次以上, 就以 0 分处理
        return 0.0


def grade_markov(pitchs, markov=None):
    mktb = markov if markov else markov_table
    result = 0.0
    score = 1.0 / (len(pitchs) - 1)

    for p, n in zip(pitchs[:-1], pitchs[1:]):
        try:
            rank = mktb[p][n]  # 马尔可夫表以第一个音符为列名, 先列后行
        except KeyError:
            # 可能的异常是至少一个音高不在 markov table 中,
            # 不给分, 也不作惩罚
            pass
        else:
            result += (-1 / (1 + math.e ** (7 - rank / 2)) + 1) * score

    return result


def grade_in(pitchs):
    result = 0.0
    score = 1.0 / len(pitchs)

    punishment = 0
    for p in pitchs:
        if 36 <= p <= 69:
            result += score
        else:
            punishment += 1

    if punishment < 3:
        return result / (punishment + 1.0)  # 两个音以内不在范围内
    else:  # 两次以上, 就以 0 分处理
        return 0.0


def grade_length(bar):
    """
    小节包含的音符数, 记作其长度
    :return: 
    """
    length = len(bar)
    if length in [4, 5, 6]:
        return 1.0
    elif length in [3, 7]:
        return 0.5
    elif length in [2, 8]:
        return 0.25
    else:  # 小节长度超过 8
        return 0.0


# def grade_octave_change(bar):
#     """
#     对整体八度变化的打分
#     """
#     # todo
#     octaves = [int(note[2][0]) // 12 if note[2] is not None else None for note
#                in bar]
#     if util.is_monotone(octaves):
#         if util.is_strict_monotone(octaves):
#             return 0.5
#         else:
#             return 0
#     else:
#         return 1.0


# def grade_duration_change(bar):
#     """
#     对整体时值变化的打分
#     """
#     # todo
#     durations = [note[1] for note in bar]
#     if util.is_monotone(durations):
#         if util.is_strict_monotone(durations):
#             return 0.5
#         else:
#             return 0
#     else:
#         return 1.0


def grade_change(seq):
    cur = seq[0]  # 当前元素
    count = 1
    for i in seq[1:]:
        if i == cur:
            count += 1
        else:
            cur = i
            count = 1
        if count >= 3:  # 连续 3 个元素相同, 缺少变化
            return 0.0
    return 1.0


def grade_diversity(seq):
    """
    长度为 3, 4, 则不同元素的数量至少为 2
    长度为 5, 6, 不同元素的数量至少为 3
    长度为 7, 8, 不同元素的数量至少为 4
    因此, 取两倍关系
    :return: 
    """
    print(seq)
    return 1.0 if len(set(seq)) * 2 >= len(seq) else 0.0


def evaluate_bar(bar):
    # todo - kinds of evalute ways
    if len(bar) == 1:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    try:
        durations, pitchs = zip(*[math.modf(note) for note in bar])
    except:
        print(bar)
        raise

    pitchs = [int(pitch) for pitch in pitchs]
    octaves, names = zip(*[divmod(pitch, 12) for pitch in pitchs])
    durations = [int(round(duration * 100)) for duration in durations]

    # pitch_pairs, pitch_name_pairs, octave_pairs, duration_pairs = map(
    #     util.get_order_pair, (pitchs, pitch_names, octaves, durations)
    # )

    g_chord = grade_chord(names)
    g_interval = grade_interval(pitchs)
    g_duration = grade_duration(durations)
    g_markov = grade_markov(pitchs)
    g_in = grade_in(pitchs)
    g_length = grade_length(bar)
    g_change = grade_change(bar)
    g_diversity = grade_diversity(bar)
    # g_pitch_change = grade_change(pitchs)
    # g_duration_change = grade_change(durations)
    # g_pitch_diversity = grade_diversity(pitchs)
    # g_duration_diversity = grade_diversity(durations)
    # if 0.0 in (g_chord, g_interval, g_duration, g_markov, g_in, g_length, g_change, g_diversity):
    #     print("A", g_chord, g_interval, g_duration, g_markov, g_in, g_length, g_change, g_diversity)
    #     return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    print("B", g_chord, g_interval, g_duration, g_markov, g_in, g_length, g_change, g_diversity)
    return g_chord, g_interval, g_duration, g_markov, g_in, g_length, g_change, g_diversity
