# -*- coding: utf-8 -*-

from __future__ import absolute_import

import random

from mingus.containers import Bar, Note

from collections import Sequence

import gen

__author__ = "kissg"
__date__ = "2017-03-29"


def mutate_bar(individual, indpb=0.1, ppb=None, dpb=None):
    mutation_method = __method2__ if not ppb and not dpb else __method__
    func = getattr(BarMutation, random.choice(mutation_method))
    return func(individual, indpb, ppb, dpb)


def mutate_sentence(individual):
    for i in xrange(len(individual)):
        if random.random() < 0.5:
            individual[i] = gen.get_bar(individual.bars_pool)
    return individual,


class BarMutation(object):
    @classmethod
    def mut_name(cls, individual, indpb=0.1, ppd=None, dpb=None):
        # 不用 for x in individual 的原因是, 要最 individual 本身进行修改
        for i in xrange(len(individual)):
            if random.random() < indpb:
                individual[i] = gen.gen_pitch(p=ppd)  # update Note
        return individual,

    @classmethod
    def mut_augment(cls, individual, indpb=0.1, ppd=None, dpb=None):
        for i in xrange(len(individual)):
            if individual[i][2] is not None and random.random() < indpb:
                individual[i][2][0].augment()  # Note.augment
                # 将音符转换成标准的科学表示法
                individual[i][2][0].from_hertz(individual[i][2][0].to_hertz())
            return individual,

    @classmethod
    def mut_diminish(cls, individual, indpb=0.1, ppd=None, dpb=None):
        for i in xrange(len(individual)):
            if individual[i][2] is not None and random.random() < indpb:
                individual[i][2][0].diminish()  # Note.augment
                individual[i][2][0].from_hertz(individual[i][2][0].to_hertz())
        return individual,

    @classmethod
    def mut_transpose(cls, individual, indpb=0.1, ppd=None, dpb=None):
        for i in xrange(len(individual)):
            if individual[i][2] is not None and random.random() < indpb:
                # transpose - 指定度数, 转换音名. 第二个参数决定升高还是降低
                individual[i][2][0].transpose(str(random.randint(1, 7)),
                                              random.choice([True, False]))
                individual[i][2][0].from_hertz(individual[i][2][0].to_hertz())
        return individual,

    @classmethod
    def mut_duration(cls, individual, indpb=0.1, ppd=None, dpb=None):
        for i in xrange(len(individual) - 1, -1, -1):  # 从尾音符开始
            if random.random() < indpb:  # None, 休止符也有时值的概念
                individual.change_note_duration(individual[i][0],
                                                gen.gen_duration(p=dpb))
        return individual,


__method__ = ["mut_name", "mut_duration"]
__method2__ = ["mut_name", "mut_augment", "mut_diminish", "mut_transpose",
               "mut_duration"]
__all__ = ["mutate_bar", "mutate_sentence"]
