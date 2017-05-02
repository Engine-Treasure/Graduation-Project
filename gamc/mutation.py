# -*- coding: utf-8 -*-

import random
import array
import math
from deap import creator

from mingus.containers import Bar, Note

from collections import Sequence

import gen

__author__ = "kissg"
__date__ = "2017-03-29"


__mutation_bar__ = [
    "mut_none_bar",
    "mut_reverse_bar",
    "mut_rotate_right_bar",
    "mut_invert_pitch_bar",
    "mut_ascend_pitch_bar",
    "mut_transpose_bar",
    "mut_descend_pitch_bar",
    "mut_regenerate_bar"
]


def mutate_bar(individual):
    mutation_method = __mutation_bar__
    func = getattr(MutationBar, random.choice(mutation_method))
    return func(individual)


class MutationBar(object):
    @classmethod
    def mut_none_bar(cls, ind_bar):
        """
        :return: bar individual itself
        """
        return ind_bar,

    @classmethod
    def mut_regenerate_bar(cls, ind_bar):
        bar = gen.init_bar()
        return ind_bar,

    @classmethod
    def mut_reverse_bar(cls, ind_bar):
        """
        :return: reversed bar individual
        """
        ind_bar.reverse()
        return ind_bar,

    @classmethod
    def mut_rotate_right_bar(cls, ind_bar):
        """
        :return: 
        """
        # todo: should make n a paarmeter?
        # randint - including both end points.
        n = random.randint(0, len(ind_bar) - 1)
        ind_bar = ind_bar[-n:] + ind_bar[:-n]
        return ind_bar,

    @classmethod
    def mut_invert_pitch_bar(cls, ind_bar):
        """
        :return: 将音高倒置, 围绕中央 C (48)
        """
        durations, pitchs = zip(*[math.modf(note) for note in ind_bar])
        pitchs = [96 - p for p in pitchs]
        # Notice - ind_bar is a instance of array.array
        return creator.Bar([p + d for p, d in zip(pitchs, durations)]),

    @classmethod
    def mut_ascend_pitch_bar(cls, ind_bar):
        """
        :return: 
        """
        ind_bar = sorted(ind_bar, key=lambda t: int(t))
        return creator.Bar(ind_bar),

    @classmethod
    def mut_descend_pitch_bar(cls, ind_bar):
        """
        :return: 
        """
        ind_bar = sorted(ind_bar, key=lambda t: int(t), reverse=True)
        return creator.Bar(ind_bar),

    @classmethod
    def mut_transpose_bar(cls, ind_bar):
        """
        :return: 
        """
        n = random.randint(1, 4)  # randint - including both end points.

        durations, pitchs = zip(*[math.modf(note) for note in ind_bar])
        ls = [p + n + d if p + n < 97 else 192 - p - n + d for p, d in
              zip(pitchs, durations)]
        # return array.array("d", ls),
        return creator.Bar(ls),

    # @classmethod
    # def mut_delete_bar(self, ind_bar):
    #     """
    #     :return:
    #     """
    #     n = random.randint(1, 4)  # randint - including both end points.
    #
    #     durations, pitchs = zip(*[math.modf(note) for note in ind_bar])
    #     ls = [p + n + d if p + n < 97 else 192 - p - n + d for p, d in
    #           zip(pitchs, durations)]
    #     # return array.array("d", ls),
    #     return creator.Bar(ls),

def mutate_sentence(individual):
    for i in xrange(len(individual)):
        if random.random() < 0.5:
            individual[i] = gen.get_bar(individual.bars_pool)
    return individual,


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


__method__ = ["mut_name", "mut_duration"]
__method2__ = ["mut_name"]
# __method2__ = ["mut_name", "mut_augment", "mut_diminish", "mut_transpose",
#                "mut_duration"]
__all__ = ["mutate_bar", "mutate_sentence"]
