# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-29"

import random

from mingus.containers import Bar, Note

from collections import Sequence

from src import gen


def mutate(individual, indpb):
    func = getattr(Mutation, random.choice(__method__))
    print(func)
    return func(individual, indpb)


class Mutation(object):
    @classmethod
    def mut_name(cls, individual, indpb):
        for i in xrange(len(individual)):
            if random.random() < indpb:
                individual[i] = gen.gen_pitch()  # update Note
        return individual,

    @classmethod
    def mut_augment(cls, individual, indpb):
        for i in xrange(len(individual)):
            if individual[i][2] is not None and random.random() < indpb:
                individual[i][2][0].augment()  # Note.augment
            return individual,

    @classmethod
    def mut_diminish(cls, individual, indpb):
        for i in xrange(len(individual)):
            if individual[i][2] is not None and random.random() < indpb:
                individual[i][2][0].diminish()  # Note.augment
        return individual,

    @classmethod
    def mut_transpose(cls, individual, indpb):
        for i in xrange(len(individual)):
            if individual[i][2] is not None and random.random() < indpb:
                individual[i][2][0].transpose(str(random.randint(1, 7)))
        return individual,


__method__ = ["mut_name", "mut_augment", "mut_diminish", "mut_transpose"]
__all__ = ["mutate"]
