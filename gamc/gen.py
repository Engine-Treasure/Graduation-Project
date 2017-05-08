# -*- coding: utf-8 -*-
from __future__ import division

import math
from copy import deepcopy

import numpy as np
from deap import creator

from statistics import duration_frequencies as duration_probability

__author__ = "kissg"
__date__ = "2017-03-31"


DURATION_RANGE = [1, 2, 4, 8, 16, 32]


def get_pitch():
    # return random.randint(low, up)
    # pitch = np.random.choice(range(0, 88), p=pitch_probability)
    # return pitch if 36 <= pitch <= 83 else get_pitch()
    # pitch = np.random.choice([
    #     45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67
    # ])
    pitch = np.random.choice([
        36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65,
        67, 69
    ])
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
            [dt for dt in range(int(math.ceil(1 / rest)), 65, 1) if
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
