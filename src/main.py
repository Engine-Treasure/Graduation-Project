# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-10"

import random
from math import ceil

import numpy as np
import mingus.extra.lilypond as lp
from deap import base
from deap import tools
from deap import creator
from mingus.containers import Bar, Note, Track
from mingus.midi import midi_file_out

from util import get_geometric_progression_of_2

VELOCITY = {16, 33, 49, 64, 80, 96, 112, 126}

# 适应度函数, `weights` weights 的每一项表示一个观测值
# 暂定为 (1.0,), 表示最大化协和度
creator.create("BarFitness", base.Fitness, weights=(1.0,))
creator.create("TrackFitness", base.Fitness, weights=(1.0,))

# 以小节为个体
# [[1, 5, 4], [1.5, 5, 4], [3, 5, 4], [5, 5, 4]]
creator.create("Bar", Bar, fitness=creator.BarFitness)
creator.create("Track", Track, fitness=creator.TrackFitness)


def gen_note(min=0, max=107):
    '''
    :param min: minimum scientific note name
    :param max: maximum scientific note name
    :return: mingus.containers.Note
    '''
    return Note().from_int(np.random.choice(range(min, max + 1)))


def gen_duration(min=64, max=1):
    '''
    The parameters may be confusing. However 1 represents a whote note ,
    2 a half note, 4 a quarter note, etc.
    :return: a duration of note
    '''
    return np.random.choice(get_geometric_progression_of_2(max, min))


def gen_bar(key="C", meter=(4, 4)):
    bar = Bar(key, meter)
    while not bar.is_full():
        bar.place_notes(toolbox.note(),
                        gen_duration(max=int(ceil(bar.value_left()))))
    return bar



def evalute_bar(bar):
    pass


def evaluate_track(individual):
    # Do some hard computing on the individual
    # Multi dimension
    return 1



def gen_track(bars):
    track = Track()
    for bar in bars:
        track.add_bar(bar)
    return track


toolbox = base.Toolbox()
# 此处随机生成种群的个体
# 注: toolbox.register(alias, func, args_for_func)
# 注: tools.initRepeat(container, generator_func, repeat_times)
toolbox.register("note", gen_note, min=9, max=96)  # 钢琴共 88 键, A0 ~ C8
toolbox.register("bar", gen_bar, key="C", meter=(4, 4))
toolbox.register("track", gen_track)

bars = [toolbox.bar() for i in range(1)]
track = toolbox.track(bars)
lp.to_pdf(lp.from_Track(track), "1.pdf")


midi_file_out.write_Track("1.mid", track)
