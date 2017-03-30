# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-29"

import random

from mingus.containers import Bar, Note

from collections import Sequence


def mutPitch(individual, indpb):
    size = len(individual)
    for i in xrange(size):
        if random.random() < indpb:
            pos = individual[i][0]
            individual.place_notes_at(10, pos)
            print(individual)
    return individual
