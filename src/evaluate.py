# -*- coding: utf-8 -*-


from __future__ import division

from mingus.core import intervals

import util

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
    if "unison" in itv:  # 纯一度, 纯八度
        return 10
    elif itv in ("perfect fifth", "perfect fourth"):
        return 8
    elif itv in ("major third", "minor third", "major sixth", "minor sixth"):
        return 6
    elif itv in ("major second", "minor second", "major seventh",
                 "minor seventh"):
        return 3
    else:
        return 0


def grade_octave(octaves_pair):
    """
    对八度打分 - 度数小于在一个八度内的, 打 1 分； 否则 0 分
    """
    if abs(octaves_pair[0] - octaves_pair[1]) < 2:
        return 1
    else:
        return 0


def grade_duration(durations_pair):
    """
    对时值打分 - 时值变化剧烈 (超过 4 倍), 0 分
    """
    duration1, duration2 = durations_pair
    if max(duration1 / duration2, duration2 / duration1) > 4:
        return 0
    else:
        return 1


def grade_pitch_change(bar):
    """
    对整体音高变化的打分 - 单调变化或不变的音高, 低分
    """
    # todo
    pitches = [int(note[2][0]) for note in bar]
    return 0 if util.is_monotone(pitches) else 1


def grade_duration_change(bar):
    """
    对整体时值变化的打分 - 单调的时值, 缺少节奏感, 低分
    """
    # todo
    durations = [note[1] for note in bar]
    return 0 if util.is_monotone(durations) else 1


def grade_internal_chords(bar):
    """
    对调内三/七和弦的打分
    """
    # todo
    pass


def grade_markov(bar):
    # todo
    pass


def evalute_bar(bar):
    # todo - kinds of evalute ways
    names, octaves, durations = util.get_names_octaves_durations(bar)

    # 可能生成了单音符的小节, 直接返回 1 分, 不做评价
    if len(names) == 1:
        return 1.0
    # 音名, 八度, 时值的组合, 每一对都是前后组合, 有别于 Python 自带的 Combinations
    name_combinations, octave_combinations, duration_combinations = map(
        util.get_combination_order2, (names, octaves, durations))

    # 以下打分是针对每一对组合的
    grade_of_intervals = map(grade_intervals, name_combinations)
    grade_of_octave = map(grade_octave, octave_combinations)
    grade_of_duration = map(grade_duration, duration_combinations)

    # 评分求和, 并标准化为 0~1.0, scaling
    grade_of_intervals = sum(grade_of_octave) / 10 / len(grade_of_intervals)
    grade_of_octave = sum(grade_of_octave) / len(grade_of_octave)
    grade_of_duration = sum(grade_of_duration) / len(grade_of_duration)

    # 以下打分是针对整个小节的, 不必求和
    grade_of_pitch_change = grade_pitch_change(bar)
    grade_of_duration_change = grade_duration_change(bar)

    return grade_of_intervals, grade_of_octave, grade_of_duration, \
           grade_of_pitch_change, grade_of_duration_change
    # simply mean
    # return sum((grade_of_intervals, grade_of_octave, grade_of_duration,
    #             grade_of_pitch_change, grade_of_duration_change)) / 5.0
    # grade_of_duration_change
    # grade_of_internal_chords
    # grade_of_pitch_change


def evaluate_track(individual):
    # Do some hard computing on the individual
    # Multi dimension
    return 1
