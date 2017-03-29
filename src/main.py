# -*- coding: utf-8 -*-

from __future__ import division

from collections import OrderedDict
from itertools import islice
from math import ceil

import mingus.core.intervals as intervals
import mingus.extra.lilypond as lp
import numpy as np
from deap import base
from deap import creator
from deap import tools
from mingus.containers import Bar, Note, Track
from mingus.midi import midi_file_out

import util
from config import pitch_frequencies, duration_frequencies

__author__ = "kissg"
__date__ = "2017-03-10"

VELOCITY = {16, 33, 49, 64, 80, 96, 112, 126}  # 音的强度


def gen_pitch(min=0, max=107):
    """
    :param min: min pitch
    :param max: max pitch
    :return: mingus.containers.Note
    """
    return Note().from_int(
        np.random.choice(range(min, max + 1), p=pitch_frequencies))
    # np.random.choice(range(min, max + 1)))


def gen_duration(min=32, max=1):
    """
    The parameters may be confusing. However 1 represents a whole note,
    2 a half note, 4 a quarter note, etc.
    :return: a duration of note
    """
    # 公比是 2 的等比数列, 表示可用的时值
    available_durations = util.get_geometric_progression_of_2(max, min)
    # duration_frequencies 是按 1, 2, 4, 8, ... 顺序排列的
    probabilities = duration_frequencies[-len(available_durations):]
    p_sum = sum(probabilities)
    p = [_ / p_sum for _ in probabilities]  # 重新计算比例

    # todo - better probabilities
    return np.random.choice(available_durations, p=p)


def gen_bar(key="C", meter=(4, 4)):
    bar = creator.Bar(key, meter)
    while not bar.is_full():
        # todo - place rest
        bar.place_notes(toolbox.pitch(),
                        gen_duration(max=int(ceil(bar.value_left()))))
    return bar


def gen_track(bars):
    # todo - another approach
    track = creator.Track()
    for bar in bars:
        track.add_bar(bar)
    return track


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


creator.create("BarFitness", base.Fitness, weights=(1.0, 1.0, 1.0, 1.0, 1.0))
creator.create("TrackFitness", base.Fitness, weights=(1.0,))

creator.create("Bar", Bar, fitness=creator.BarFitness)
creator.create("Track", Track, fitness=creator.TrackFitness)

toolbox = base.Toolbox()
# 此处随机生成种群的个体
# 注: toolbox.register(alias, func, args_for_func)
# 注: tools.initRepeat(container, generator_func, repeat_times)
toolbox.register("pitch", gen_pitch, min=9, max=96)  # 钢琴共 88 键, A0 ~ C8
toolbox.register("bar", gen_bar, key="C", meter=(4, 4))
toolbox.register("track", gen_track)


toolbox.register("mate", )
toolbox.register("mutate", )
toolbox.register("select", )
toolbox.register("evaluate", )


if __name__ == '__main__':
    bar_1 = toolbox.bar()
    bar_2 = toolbox.bar()
    bar_1.fitness.values = evalute_bar(bar_1)
    bar_2.fitness.values = evalute_bar(bar_2)
    print(bar_1.fitness.values)
    print(bar_2.fitness.values)
    child_1, child_2 = [toolbox.clone(ind) for ind in (bar_1, bar_2)]
    selected = tools.selBest([child_1, child_2], 1)
    print(child_1, child_2)
    print(selected)




    # bars = [toolbox.bar() for i in range(100)]
    #
    # print("E")
    # bars_with_grade = {bar: evalute_bar(bar) for bar in bars}
    # bar_rank = OrderedDict(
    #     sorted(bars_with_grade.iteritems(), key=lambda t: t[1], reverse=True))
    # print(len(bar_rank))
    # print(bar_rank.values())
    #
    # top10_bars = islice(bar_rank.keys(), 10)
    # last10_bars = islice(bar_rank.keys(), 90, 100)
    #
    # for k, v in bar_rank.iteritems():
    #     print(v, k)
    #
    # track_top = toolbox.track(top10_bars)
    # track_last = toolbox.track(last10_bars)
    #
    # lp.to_pdf(lp.from_Track(track_top), "top.pdf")
    #
    # midi_file_out.write_Track("top.mid", track_top)
    #
    # lp.to_pdf(lp.from_Track(track_last), "last.pdf")
    #
    # midi_file_out.write_Track("last.mid", track_last)

    # track = toolbox.track(bars)
    # lp.to_pdf(lp.from_Track(track), "1.pdf")
    #
    # midi_file_out.write_Track("1.mid", track)
