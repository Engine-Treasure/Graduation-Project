# -*- coding: utf-8 -*-
from __future__ import division

import random
import math
from copy import deepcopy

import numpy as np
from deap import creator
from mingus.containers import Note

import util
from statistics import duration_frequencies as duration_probability
from statistics import new_pitch_frequencies_ls as pitch_probability

__author__ = "kissg"
__date__ = "2017-03-31"

VELOCITY = {16, 33, 49, 64, 80, 96, 112, 126}  # 音的强度


def gen_pitch(_min=0, _max=88, p=None):
    """
    :param _min: min pitch, 9 - 'A-0'
    :param _max: max pitch, 96 - 'C-8'
    :param p: probability
    :return: mingus.containers.Note
    """
    if not p:
        p = pitch_probability
        pitch = Note().from_int(np.random.choice(range(_min, _max), p=p))
        # C3-B6
        return pitch if 130 < pitch.to_hertz() < 1976 else gen_pitch(_min, _max)
    else:
        return Note().from_int(np.random.choice(range(0, 88), p=p))
        # 经验设置音高, 最常用的音高区间是 C3-B5
        # return pitch if 130 < pitch.to_hertz() < 988 else gen_pitch(min, max)
        # np.random.choice(range(min, max + 1)))


def gen_duration(_min=32, _max=1, p=None):
    """
    The parameters may be confusing. However 1 represents a whole note,
    2 a half note, 4 a quarter note, etc.
    :param _min: min duration, 32 - 1/32
    :param _max: max duration, 1 - 1/1
    :return: a duration of note
    """
    if not p:
        p = duration_probability
    # 公比是 2 的等比数列, 表示可用的时值
    available_durations = util.get_geometric_progression_of_2(_max, _min)
    # duration_frequencies 是按 1, 2, 4, 8, ... 顺序排列的
    available_probability = p[-len(available_durations):]
    new_total = sum(available_probability)
    probality = [_ / new_total for _ in available_probability]  # 重新计算比例

    # todo - better probabilities
    return np.random.choice(available_durations, p=probality)
    # return np.random.choice(available_durations)


def init_bar(container, **kwargs):
    key = kwargs.get("key", "C")
    meter = kwargs.get("meter", (4, 4))

    bar = container(key, meter)
    while not bar.is_full():
        # todo - place rest
        bar.place_notes(gen_pitch(),
                        gen_duration(_max=int(math.ceil(bar.value_left()))))
    return bar


def get_bar(bars_pool):
    return random.SystemRandom().choice(bars_pool)


def init_sentence(container, **kwargs):
    sentence = container()
    bars_pool = kwargs.get("bars_pool")
    sentence.bars_pool = bars_pool
    for i in xrange(4):
        sentence.append(get_bar(sentence.bars_pool))
    return sentence


PITCH_LOW, PITCH_UP = 0, 96
DURATION_RANGE = [1, 2, 4, 8, 16, 32]


def get_pitch():
    # return random.randint(low, up)
    # pitch = np.random.choice(range(0, 88), p=pitch_probability)
    # return pitch if 36 <= pitch <= 83 else get_pitch()
    pitch = np.random.choice([
        36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65,
        67, 69
    ])
    # pitch = np.random.choice([
    #     48, 50, 52, 53, 55, 57, 59
    # ])
    return pitch


def get_duration(_range):
    available_probability = duration_probability[-len(_range):]
    new_total = sum(available_probability)
    probality = [_ / new_total for _ in available_probability]  # 重新计算比例
    duration = np.random.choice(_range, p=probality)
    return duration


def init_bar():
    rest = 1
    ind_bar = creator.Bar()
    while rest:
        pitch = get_pitch()
        duration = get_duration(
            [dt for dt in range(int(math.ceil(1 / rest)), 33, 1) if
             dt in DURATION_RANGE])
        ind_bar.append(pitch + duration / 100)
        rest -= 1 / duration
    return ind_bar


name2int = {
    "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
    "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11
}


def init_pop_from_seq(seq):
    ls = []
    rest = 1.0
    bar = creator.Bar()
    for i in seq:
        if rest - i[1] > 0.0:
            bar.append(i[0])
            rest -= i[1]
        elif rest - i[1] == 0.0:
            bar.append(i[0])
            ls.append(deepcopy(bar))
            bar = creator.Bar()
            rest = 1.0
        else:
            last_note = bar.pop()
            rest = 1.0 - sum(1.0 / math.modf(note)[0] for note in bar)
            bar.append(int(last_note) + 1.0 / rest / 100)
            ls.append(deepcopy(bar))
            bar = creator.Bar()
            bar.append(i[0])
            rest = 1.0 - i[1] if i[1] != 1.0 else 1.0
    if rest != 1.0:
        ls.append(deepcopy(bar))
    return ls
