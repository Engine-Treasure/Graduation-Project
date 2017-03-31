# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from mingus.containers import Note

import util
from config import pitch_frequencies, duration_frequencies
from math import ceil

__author__ = "kissg"
__date__ = "2017-03-31"

VELOCITY = {16, 33, 49, 64, 80, 96, 112, 126}  # 音的强度


def gen_pitch(min=9, max=96):
    """
    :param min: min pitch, 9 - 'A-0'
    :param max: max pitch, 96 - 'C-8'
    :return: mingus.containers.Note
    """
    return Note().from_int(
        # np.random.choice(range(min, max + 1), p=pitch_frequencies))
        np.random.choice(range(min, max + 1)))


def gen_duration(min=32, max=1):
    """
    The parameters may be confusing. However 1 represents a whole note,
    2 a half note, 4 a quarter note, etc.
    :param min: min duration, 32 - 1/32
    :param max: max duration, 1 - 1/1
    :return: a duration of note
    """
    # 公比是 2 的等比数列, 表示可用的时值
    available_durations = util.get_geometric_progression_of_2(max, min)
    # duration_frequencies 是按 1, 2, 4, 8, ... 顺序排列的
    probabilities = duration_frequencies[-len(available_durations):]
    p_sum = sum(probabilities)
    p = [_ / p_sum for _ in probabilities]  # 重新计算比例

    # todo - better probabilities
    # return np.random.choice(available_durations, p=p)
    return np.random.choice(available_durations)


def init_bar(container, **kwargs):
    key = kwargs.get("key", "C")
    meter = kwargs.get("meter", (4, 4))

    bar = container(key, meter)
    while not bar.is_full():
        # todo - place rest
        bar.place_notes(gen_pitch(),
                        gen_duration(max=int(ceil(bar.value_left()))))
    return bar


def init_track(container, **kwargs):
    # todo - another approach
    track = container()
    # for bar in bars:
    #     track.add_bar(bar)
    # return track
