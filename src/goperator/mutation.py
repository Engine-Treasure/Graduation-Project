# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-29"

import random

from mingus.containers import Bar, Note

from collections import Sequence

from src import gen


def mut_name(individual, indpb):
    for i in xrange(len(individual)):
        if random.random() < indpb:
            individual[i] = gen.gen_pitch()
    return individual,


def mut_augment(individual, indpb):
    if random.random() < indpb:
        individual.augment()
    return individual,


def mut_diminish(individual, indpb):
    if random.random() < indpb:
        individual.diminish()
    return individual,


def mut_transpose(individual, indpb):
    if random.random() < indpb:
        individual.diminish()
    return individual,

