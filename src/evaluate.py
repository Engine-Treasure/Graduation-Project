# -*- coding: utf-8 -*-


from __future__ import division

from math import sqrt, floor

from mingus.core import intervals
from mingus.containers import Note

import util
from config import markov_table_rank

__author__ = "kissg"
__date__ = "2017-03-30"


def grade_intervals(notes_pair):
    """
    对音程打分 -
    纯一度或纯八度, 为极协和音程,
    纯四度或纯五度, 协和音程,
    大三度, 小三度, 大六度, 小六度, 不完全协和音程
    以上属于相对协和音程
    大二度, 小二度, 大七度, 小七度, 不协和音程
    其他为极不协和音程
    """
    itv = intervals.determine(*notes_pair)
    if "unison" in itv:  # 纯一度, 纯八度, 缺少变化
        return 1
    elif itv in ("perfect fifth", "perfect fourth"):
        return 5
    elif itv in ("major third", "minor third", "major sixth", "minor sixth"):
        return 3
    elif itv in ("major second", "minor second", "major seventh",
                 "minor seventh"):
        return -1
    else:
        return -2


def grade_octave(octaves_pair):
    """
    对八度打分 - 度数在一个八度内的, 打 1 分； 否则 0 分
    """
    if abs(octaves_pair[0] - octaves_pair[1]) <= 1:
        return 1
    else:
        return 0


def grade_duration(durations_pair):
    """
    对时值打分 - 时值变化剧烈 (超过 4 倍), -1 分
    """
    duration1, duration2 = durations_pair
    if max(duration1 / duration2, duration2 / duration1) > 4:
        return -1
    else:
        return 1


def grade_markov(notes_pair):
    try:
        rank = markov_table_rank[notes_pair[0]][notes_pair[1]]
    except KeyError:  # 可能的异常是至少一个音高不在 markov table 中, 标记为异常音高, 打 0 分
        return -1
    else:
        return 1 / sqrt(rank)


def grade_pitch_change(bar):
    """
    对整体音高变化的打分 - 单调变化或不变的音高, 扣分
    """
    # todo
    pitches = [int(note[2][0]) for note in bar if note[2] is not None]
    return -1 if util.is_monotone(pitches) else 1


def grade_duration_change(bar):
    """
    对整体时值变化的打分 - 单调的时值, 缺少节奏感, 扣分
    """
    # todo
    durations = [note[1] for note in bar]
    return -1 if util.is_monotone(durations) else 1


def grade_bar_length(bar):
    length = len(bar)
    if length in [4]:
        return 1.0
    elif length in [3, 5]:
        return 0.7
    elif length in [2, 6]:
        return 0.3
    else:  # 一个小节中音符过多，扣分
        return -0.2


def grade_internal_chords(bar):
    """
    对调内三/七和弦的打分
    """
    # todo
    # names, octaves, durations = util.GET_NAMES_OCTAVES_DURATIONS(bar)
    pass


def evaluate_bar(bar):
    # todo - kinds of evalute ways
    names, octaves, durations = util.get_names_octaves_durations(bar)

    # 可能生成了单音符的小节, 直接返回 1 分, 不做评价
    if len(names) == 1:
        return (0.0,) * 7
    # 音名, 八度, 时值的组合, 每一对都是前后组合, 有别于 Python 自带的 Combinations
    name_combinations, octave_combinations, duration_combinations = map(
        util.get_combination_order2, (names, octaves, durations))

    nos = [n + "-" + str(o) for n, o in zip(names, octaves)]
    name_octave_combinations = util.get_combination_order2(nos)

    # 以下打分是针对每一对组合的
    grade_of_intervals = map(grade_intervals, name_combinations)
    grade_of_octave = map(grade_octave, octave_combinations)
    grade_of_duration = map(grade_duration, duration_combinations)
    grade_of_markov = map(grade_markov, name_octave_combinations)

    # 评分求和, 并标准化为 0~1.0, scaling
    grade_of_intervals = sum(grade_of_intervals) / 10 / len(grade_of_intervals)
    grade_of_octave = sum(grade_of_octave) / len(grade_of_octave)
    grade_of_duration = sum(grade_of_duration) / len(grade_of_duration)
    grade_of_markov = sum(grade_of_markov) / len(grade_of_markov)

    # 以下打分是针对整个小节的, 不必求和
    grade_of_pitch_change = grade_pitch_change(bar)
    grade_of_duration_change = grade_duration_change(bar)
    grade_of_bar_length = grade_bar_length(bar)

    print(
        grade_of_intervals, grade_of_octave, grade_of_duration, grade_of_markov,
        grade_of_pitch_change,
        grade_of_duration_change, grade_of_bar_length)
    return grade_of_intervals, grade_of_octave, grade_of_duration, grade_of_markov, \
           grade_of_pitch_change, grade_of_duration_change, grade_of_bar_length
    # simply mean
    # return sum((grade_of_intervals, grade_of_octave, grade_of_duration,
    #             grade_of_pitch_change, grade_of_duration_change)) / 5.0
    # grade_of_duration_change
    # grade_of_internal_chords
    # grade_of_pitch_change


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


def grade_name_change_similarity(name_change_pair):
    result = 1.0
    cor_pair = zip(name_change_pair[0], name_change_pair[1])
    for p1, p2 in cor_pair:
        if p1 == p2:
            continue
    pass


def evaluate_sentence(sentence):
    array_length = map(len, sentence)
    try:
        array_names, array_octaves, array_durations = zip(
            *map(util.get_names_octaves_durations, sentence))
    except:
        print(sentence)
        raise
    array_name_changes = map(get_name_change, array_names)
    array_octave_change = map(get_octave_change, array_octaves)
    array_duration_change = map(get_duration_change, array_durations)

    al_combinations, an_combinations, ao_combinations, ad_combinations, \
    anc_combinations, aoc_combinations, adc_combinations = map(
        util.get_combination_order2, (array_length, array_names,
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

    try:
        g_length_similarity, g_name_similarity, g_octave_similarity, \
        g_duration_similarity, g_nct_similarity, g_oct_similarity, \
        g_dct_similarity = [sum(x) / len(x) for x in [
            grade_of_length_similarity, grade_of_name_similarity,
            grade_of_octave_similarity, grade_of_duration_similarity,
            grade_of_nct_similarity, grade_of_oct_similarity,
            grade_of_dct_similarity] if x != 0]
    except:
        print(grade_of_length_similarity, grade_of_name_similarity, grade_of_octave_similarity,
        grade_of_duration_similarity, grade_of_nct_similarity, grade_of_oct_similarity,
        grade_of_dct_similarity)
        raise

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
