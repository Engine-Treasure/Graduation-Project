# -*- coding: utf-8 -*-


from __future__ import division

import math

import numpy as np
from mingus.core import intervals
from mingus.containers import Note

import util
from common import get_names_octaves_durations
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
    音程过大的, 惩罚性扣分
    """
    diff = abs(pitch_piar[0] - pitch_piar[1])
    if diff < 8:
        return 1.0
    elif diff <= 10:
        return 0.2
    elif diff <= 12:
        return 0.0
    else:
        return -1.0  # 音程超过 12 度, 严惩


def grade_octave(octave_diffrence):
    """
    不同八度, 音的差别较大, 八度相差越大, 音变化越剧烈, 刺耳
    """
    if not octave_diffrence:  # 同一个八度
        return 1.0
    elif abs(octave_diffrence) == 1:  # 差一个八度
        return 0.75
    elif abs(octave_diffrence) == 2:
        return 0.25
    elif abs(octave_diffrence) == 3:
        return 0.0
    else:
        return -0.25


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
        return -1.0  # 音值变化超过 4 倍, 严惩


def grade_markov(pitch_pair, markov=None):
    mktb = markov if markov else markov_table
    try:
        rank = mktb[pitch_pair[0]][pitch_pair[1]]
    except KeyError:
        # 可能的异常是至少一个音高不在 markov table 中, 标记为异常音高, 打 0 分接口
        return 0.0
    else:
        if rank >= 25:
            return -1  # 严惩
        else:
            return -1 / (1 + math.e ** (7 - rank / 2)) + 1


def grade_pitch_change(bar):
    """
    对整体音高变化的打分
    """
    # todo
    pitches = [int(note[2][0]) if note[2] is not None else None for note in bar]
    if util.is_monotone(pitches):
        if util.is_strict_monotone(pitches):
            return 0.5
        else:
            return 0
    else:
        return 1.0


def grade_octave_change(bar):
    """
    对整体八度变化的打分
    """
    # todo
    octaves = [int(note[2][0]) // 12 if note[2] is not None else None for note
               in bar]
    if util.is_monotone(octaves):
        if util.is_strict_monotone(octaves):
            return 0.5
        else:
            return 0
    else:
        return 1.0


def grade_duration_change(bar):
    """
    对整体时值变化的打分
    """
    # todo
    durations = [note[1] for note in bar]
    if util.is_monotone(durations):
        if util.is_strict_monotone(durations):
            return 0.5
        else:
            return 0
    else:
        return 1.0


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
        return 0.0
    elif length >= 8:  # 极端情况, 扣分
        return -1.0


def evaluate_bar(bar):
    # todo - kinds of evalute ways
    if len(bar) == 1:
        return 0, 0, 0, 0, 0

    durations, pitchs = zip(*[math.modf(note) for note in bar])

    pitchs = [int(pitch) for pitch in pitchs]
    octaves, pitch_names = zip(*[divmod(pitch, 12) for pitch in pitchs])
    durations = [int(round(duration * 100)) for duration in durations]

    pitch_pairs, pitch_name_pairs, octave_pairs, duration_pairs = map(
        util.get_order_pair, (pitchs, pitch_names, octaves, durations)
    )
    g_chord = np.mean([grade_chord(pn) for pn in pitch_name_pairs])
    g_interval = np.mean([grade_interval(p) for p in pitch_pairs])
    g_duration = np.mean([grade_duration(d) for d in duration_pairs])
    g_markov = np.mean([grade_markov(p) for p in pitch_pairs])
    g_length = np.mean(grade_length(bar))

    return g_chord, g_interval, g_duration, g_markov, g_length


def grade_length_similarity(length_pair):
    """乐句的长度相似度"""
    distance = abs(length_pair[0] - length_pair[1])
    return 1.0 - distance * 0.25 if distance <= 4 else -0.25


def grade_name_similarity(name_pair):
    result = 1.0
    # zip short
    cor_pair = zip(name_pair[0], name_pair[1])
    for p1, p2 in cor_pair:
        result -= 0.25 if p1 != p2 else 0
    return result if result > -1.0 else -1.0


def grade_octave_similarity(octave_pair):
    result = 1.0
    cor_pair = zip(octave_pair[0], octave_pair[1])
    for p1, p2 in cor_pair:
        if p1 == p2:
            continue
        elif abs(p1 - p2) == 1:
            result -= 0.1
        elif abs(p1 - p2) == 2:
            result -= 0.15
        else:
            result -= 0.3
    return result if result > -1.0 else -1.0


def grade_duration_similarity(duration_pair):
    result = 1.0
    cor_pair = zip(duration_pair[0], duration_pair[1])
    for p1, p2 in cor_pair:
        if p1 == p2:
            continue
        elif p1 / p2 in (2.0, 0.5):
            result -= 0.1
        elif p1 / p2 in (4.0, 0.25):
            result -= 0.15
        else:
            result -= 0.3
    return result if result > -1.0 else -1.0


def grade_nod_change_trend_similarity(nod_change_pair):
    result = 1.0
    cor_pair = zip(nod_change_pair[0], nod_change_pair[1])
    for p1, p2 in cor_pair:
        if p1 == p2:
            continue
        else:
            result -= 0.3
    return result if result > -1.0 else -1.0


def evaluate_sentence(sentence):
    array_length = map(len, sentence)
    array_names, array_octaves, array_durations = zip(
        *map(get_names_octaves_durations, sentence))
    array_name_changes = map(get_name_change, array_names)
    array_octave_change = map(get_octave_change, array_octaves)
    array_duration_change = map(get_duration_change, array_durations)

    al_combinations, an_combinations, ao_combinations, ad_combinations, \
    anc_combinations, aoc_combinations, adc_combinations = map(
        util.get_order_pair, (array_length, array_names,
                              array_octaves, array_durations,
                              array_name_changes, array_octave_change,
                              array_duration_change))

    grade_of_length_similarity = map(grade_length_similarity, al_combinations)
    grade_of_name_similarity = map(grade_name_similarity, an_combinations)
    grade_of_octave_similarity = map(grade_octave_similarity, ao_combinations)
    grade_of_duration_similarity = map(grade_duration_similarity,
                                       ad_combinations)
    grade_of_nct_similarity = map(grade_nod_change_trend_similarity,
                                  anc_combinations)
    grade_of_oct_similarity = map(grade_nod_change_trend_similarity,
                                  aoc_combinations)
    grade_of_dct_similarity = map(grade_nod_change_trend_similarity,
                                  adc_combinations)

    g_length_similarity, g_name_similarity, g_octave_similarity, \
    g_duration_similarity, g_nct_similarity, g_oct_similarity, \
    g_dct_similarity = [sum(x) / len(x) for x in [
        grade_of_length_similarity, grade_of_name_similarity,
        grade_of_octave_similarity, grade_of_duration_similarity,
        grade_of_nct_similarity, grade_of_oct_similarity,
        grade_of_dct_similarity] if len(x) != 0]

    return g_length_similarity, g_name_similarity, g_octave_similarity, \
           g_duration_similarity, g_nct_similarity, g_oct_similarity, \
           g_dct_similarity


def get_name_change(array_name):
    result = []
    for p, n in zip(array_name[:-1], array_name[1:]):
        result.append(Note(p).measure(Note(n)))
    return [r / abs(r) if r != 0 else 0 for r in result]
    # return result


def get_octave_change(array_octave):
    result = []
    for p, n in zip(array_octave[:-1], array_octave[1:]):
        result.append(p - n)
    return [r / abs(r) if r != 0 else 0 for r in result]
    # return result


def get_duration_change(array_duration):
    result = []
    for p, n in zip(array_duration[:-1], array_duration[1:]):
        result.append(p / n)
    return [floor(r - 1.0) for r in result]
    # return result
