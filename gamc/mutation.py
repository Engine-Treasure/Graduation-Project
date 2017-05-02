# -*- coding: utf-8 -*-

import random
import math

from mingus.containers import Bar, Note
from deap import creator

from collections import Sequence

import gen

__author__ = "kissg"
__date__ = "2017-03-29"


def mutate_bar(individual, indpb=0.1, ppb=None, dpb=None):
    mutation_method = __method__ if not ppb and not dpb else __method__
    func = getattr(BarMutation, random.choice(mutation_method))
    print(func)
    return func(individual)

__method__ = [
    "mut_none_bar",
    "mut_reverse_bar",
    "mut_rotate_right_bar",
    "mut_invert_pitch_bar",
    "mut_ascend_pitch_bar",
    "mut_descend_pitch_bar",
    "mut_transpose_bar",
]


def mutate_sentence(individual):
    for i in xrange(len(individual)):
        if random.random() < 0.5:
            individual[i] = gen.get_bar(individual.bars_pool)
    return individual,


class BarMutation(object):
    @classmethod
    def mut_none_bar(self, ind_bar):
        """
        :return: bar individual itself
        """
        return ind_bar,

    @classmethod
    def mut_reverse_bar(self, ind_bar):
        """
        :return: reversed bar individual
        """
        bar = creator.Bar()
        for i in ind_bar[-1::-1]:
            if i[2]:
                bar.place_notes(i[2][0], i[1])
            else:
                bar.place_notes(None, i[1])
        return bar,

    @classmethod
    def mut_rotate_right_bar(self, ind_bar):
        """
        :return: 
        """
        # todo: should make n a paarmeter?
        # randint - including both end points.
        n = random.randint(0, len(ind_bar) - 1)
        bar = creator.Bar()
        for i in ind_bar[-n:]:
            if i[2]:
                bar.place_notes(i[2][0], i[1])
        for j in ind_bar[:-n]:
            if i:
                bar.place_notes(j[2][0], j[1])
        if not bar.is_full():
            bar.place_rest(bar.value_left())
        return bar,

    @classmethod
    def mut_invert_pitch_bar(self, ind_bar):
        """
        :return: 将音高倒置, 围绕中央 C (48)
        """
        bar = creator.Bar()
        for i in ind_bar:
            if i[2]:
                bar.place_notes(Note().from_int(96 - int(i[2][0])), i[1])

        return bar,

    @classmethod
    def mut_ascend_pitch_bar(self, ind_bar):
        """
        :return: 
        """
        bar = creator.Bar()

        notes = list(ind_bar)
        notes = [n for n in notes if n[2]]
        sorted_notes = sorted(notes, key=lambda t: int(t[2][0]))
        for i in sorted_notes:
            bar.place_notes(i[2][0], i[1])
        if not bar.is_full():
            bar.place_rest(bar.value_left())
        return bar,

    @classmethod
    def mut_descend_pitch_bar(self, ind_bar):
        """
        :return: 
        """
        bar = creator.Bar()

        notes = list(ind_bar)
        notes = [n for n in notes if n[2]]
        sorted_notes = sorted(notes, key=lambda t: int(t[2][0]), reverse=True)
        for i in sorted_notes:
            bar.place_notes(i[2][0], i[1])
        if not bar.is_full():
            bar.place_rest(bar.value_left())
        return bar,

    @classmethod
    def mut_transpose_bar(self, ind_bar):
        """
        :return: 
        """
        interval = random.choice(["1", "2", "3", "4"])  # randint - including both end points.
        for cont in ind_bar:
            if cont[2]:
                cont[2][0].transpose(interval)

        bar = creator.Bar()
        for i in ind_bar:
            # 消除 b
            if i[2]:
                bar.place_notes(Note().from_hertz(i[2][0].to_hertz()), i[1])
        return bar,

# class BarMutation(object):
#     @classmethod
#     def mut_name(cls, individual, indpb=0.1, ppd=None, dpb=None):
#         # 不用 for x in individual 的原因是, 要最 individual 本身进行修改
#         for i in xrange(len(individual)):
#             if random.random() < indpb:
#                 individual[i] = gen.gen_pitch(p=ppd)  # update Note
#         return individual,
#
#     @classmethod
#     def mut_augment(cls, individual, indpb=0.1, ppd=None, dpb=None):
#         for i in xrange(len(individual)):
#             if individual[i][2] is not None and random.random() < indpb:
#                 individual[i][2][0].augment()  # Note.augment
#                 # 将音符转换成标准的科学表示法
#                 individual[i][2][0].from_hertz(individual[i][2][0].to_hertz())
#             return individual,
#
#     @classmethod
#     def mut_diminish(cls, individual, indpb=0.1, ppd=None, dpb=None):
#         for i in xrange(len(individual)):
#             if individual[i][2] is not None and random.random() < indpb:
#                 individual[i][2][0].diminish()  # Note.augment
#                 individual[i][2][0].from_hertz(individual[i][2][0].to_hertz())
#         return individual,
#
#     @classmethod
#     def mut_transpose(cls, individual, indpb=0.1, ppd=None, dpb=None):
#         for i in xrange(len(individual)):
#             if individual[i][2] is not None and random.random() < indpb:
#                 # transpose - 指定度数, 转换音名. 第二个参数决定升高还是降低
#                 individual[i][2][0].transpose(str(random.randint(1, 7)),
#                                               random.choice([True, False]))
#                 individual[i][2][0].from_hertz(individual[i][2][0].to_hertz())
#         return individual,
#
#     @classmethod
#     def mut_duration(cls, individual, indpb=0.1, ppd=None, dpb=None):
#         for i in xrange(len(individual) - 1, -1, -1):  # 从尾音符开始
#             if random.random() < indpb:  # None, 休止符也有时值的概念
#                 individual.change_note_duration(individual[i][0],
#                                                 gen.gen_duration(p=dpb))
#         return individual,


# __method__ = ["mut_name", "mut_duration"]
__method2__ = ["mut_name"]
# __method2__ = ["mut_name", "mut_augment", "mut_diminish", "mut_transpose",
#                "mut_duration"]
__all__ = ["mutate_bar", "mutate_sentence"]
