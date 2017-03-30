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
import evaluate
from goperator import crossover, mutation, selection
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

# toolbox.register("mate", )
# toolbox.register("mutate", )
# toolbox.register("select", )
# toolbox.register("evaluate", )


if __name__ == '__main__':
    bar_1 = toolbox.bar()
    bar_2 = toolbox.bar()
    # bar_1.fitness.values = evaluate.evalute_bar(bar_1)
    # bar_2.fitness.values = evaluate.evalute_bar(bar_2)
    # print(bar_1.fitness.values)
    # print(bar_2.fitness.values)
    child_1, child_2 = [toolbox.clone(ind) for ind in (bar_1, bar_2)]
    child_1, child_2 = crossover.cxOnePoint(child_1, child_2)
    print(bar_1)
    child_1 = mutation.mutPitch(child_1, 0.5)
    print(child_1)

    # selected = tools.selBest([child_1, child_2], 1)
    # print(child_1, child_2)




    # bars = [toolbox.bar() for i in range(100)]
    #
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
