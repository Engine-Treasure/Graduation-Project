# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-29"

import random

from mingus.containers import Bar, Note

from collections import Sequence

from src import gen


def mutate(individual, indpb):
    func = getattr(Mutation, random.choice(__method__))
    return func(individual, indpb)


class Mutation(object):
    @classmethod
    def mut_name(cls, individual, indpb):
        # 不用 for x in individual 的原因是, 要最 individual 本身进行修改
        for i in xrange(len(individual)):
            if random.random() < indpb:
                individual[i] = gen.gen_pitch()  # update Note
        return individual,

    @classmethod
    def mut_augment(cls, individual, indpb):
        for i in xrange(len(individual)):
            if individual[i][2] is not None and random.random() < indpb:
                individual[i][2][0].augment()  # Note.augment
                # 将音符转换成标准的科学表示法
                individual[i][2][0].from_hertz(individual[i][2][0].to_hertz())
            return individual,

    @classmethod
    def mut_diminish(cls, individual, indpb):
        for i in xrange(len(individual)):
            if individual[i][2] is not None and random.random() < indpb:
                individual[i][2][0].diminish()  # Note.augment
                individual[i][2][0].from_hertz(individual[i][2][0].to_hertz())
        return individual,

    @classmethod
    def mut_transpose(cls, individual, indpb):
        for i in xrange(len(individual)):
            if individual[i][2] is not None and random.random() < indpb:
                # transpose - 指定度数, 转换音名. 第二个参数决定升高还是降低
                individual[i][2][0].transpose(str(random.randint(1, 7)),
                                              random.choice([True, False]))
                individual[i][2][0].from_hertz(individual[i][2][0].to_hertz())
        return individual,

    @classmethod
    def mut_duration(cls, individual, indpb):
        for i in xrange(len(individual) - 1, -1, -1):  # 从尾音符开始
            if random.random() < indpb:  # None, 休止符也有时值的概念
                individual.change_note_duration(individual[i][0],
                                                gen.gen_duration())
        return individual,


__method__ = ["mut_name", "mut_augment", "mut_diminish", "mut_transpose",
              "mut_duration"]
__all__ = ["mutate"]
