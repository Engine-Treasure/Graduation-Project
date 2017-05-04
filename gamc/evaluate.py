# -*- coding: utf-8 -*-

"""
- grade_chord - 对相邻音符的协和度打分
- grade_interval - 对相邻音符的音程打分
- grade_duration - 对相邻音符的时值差打分
- grade_markov - 基于以马尔可夫表表示的作曲经验打分
- grade_range - 对音符所在区间打分
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


def grade_chord(pitch_name_pair):
    """
    对协和打分 
    纯一度或纯八度, 为极协和音程,
    纯四度或纯五度, 协和音程,
    大三度, 小三度, 大六度, 小六度, 不完全协和音程
    以上属于相对协和音程
    大二度, 小二度, 大七度, 小七度, 不协和音程
    其他为极不协和音程
    """
    dis = pitch_name_pair[1] - pitch_name_pair[0]  # 后者减前者
    res = 12 - dis * -1 if dis < 0 else dis

    # todo: 更好的评分标准
    if res == 0:  # 一度, 八度
        return 0.2
    elif res == 5:  # 四度
        return 0.6
    elif res == 7:  # 五度
        return 0.4
    elif res in [3, 4]:  # 三度
        return 1.0
    elif res in [8, 9]:  # 六度
        return 0.8
    else:  # 二度 或 七度
        return 0.0


def grade_interval(pitch_piar):
    """
    音程超过一个八度, 变化剧烈, 不和谐
    """
    diff = abs(pitch_piar[0] - pitch_piar[1])
    if diff < 8:
        return 1.0
    elif diff <= 10:
        return 0.5
    elif diff <= 12:
        return 0.25
    else:
        return 0.0  # 音程超过 12 度, 严惩


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


def grade_duration(duration_pair):
    """
    对时值打分 - 时值变化越剧烈, 越不舒服
    """
    ratio = duration_pair[1] / duration_pair[0]
    if ratio in (0.5, 1.0, 2.0):
        return 1.0
    elif ratio in (0.25, 4.0):
        return 0.2
    else:
        return 0  # 音值变化超过 4 倍, 严惩


def grade_markov(pitch_pair, markov=None):
    mktb = markov if markov else markov_table
    try:
        rank = mktb[pitch_pair[0]][pitch_pair[1]]
    except KeyError:
        # 可能的异常是至少一个音高不在 markov table 中, 标记为异常音高, 打 0 分接口
        return 0.0
    else:
        return -1 / (1 + math.e ** (7 - rank / 2)) + 1


def grade_range(pitch):
    return 1.0 if 45 <= pitch <= 67 else 0.0


def grade_length(bar):
    """
    小节包含的音符数, 记作其长度
    :return: 
    """
    length = len(bar)
    if length in [4]:
        return 1.0
    elif length in [3, 5]:
        return 0.75
    elif length == 6:
        return 0.5
    elif length in [2, 7]:
        return 0.25
    elif length >= 8:  # 极端情况, 扣分
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
    cur = 0
    count = 1
    for i in seq:
        if i == cur:
            count += 1
        else:
            cur = i
            count = 1
        if count > 3:
            return 0.0
    return 1.0


def grade_diversity(seq):
    return 0.0 if len(seq) >= 2 * len(set(seq)) else 1.0


def evaluate_bar(bar):
    # todo - kinds of evalute ways
    if len(bar) == 1:
        return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    try:
        durations, pitchs = zip(*[math.modf(note) for note in bar])
    except:
        print(bar)
        raise

    pitchs = [int(pitch) for pitch in pitchs]
    octaves, pitch_names = zip(*[divmod(pitch, 12) for pitch in pitchs])
    durations = [int(round(duration * 100)) for duration in durations]

    pitch_pairs, pitch_name_pairs, octave_pairs, duration_pairs = map(
        util.get_order_pair, (pitchs, pitch_names, octaves, durations)
    )

    # todo: 长度相关的打分
    g_chord = np.mean([grade_chord(pn) for pn in pitch_name_pairs])
    g_interval = np.mean([grade_interval(p) for p in pitch_pairs])
    g_duration = np.mean([grade_duration(d) for d in duration_pairs])
    g_markov = np.mean([grade_markov(p) for p in pitch_pairs])
    g_range = np.mean([grade_range(p) for p in pitchs])
    g_length = grade_length(bar)
    g_pitch_change = grade_change(pitchs)
    g_duration_change = grade_change(durations)
    g_pitch_diversity = grade_diversity(pitchs)
    g_duration_diversity = grade_diversity(durations)

    return g_chord, g_interval, g_duration, g_markov, g_range, g_length, g_pitch_change, \
           g_duration_change, g_pitch_diversity, g_duration_diversity
