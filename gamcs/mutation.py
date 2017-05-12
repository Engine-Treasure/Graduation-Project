# -*- coding: utf-8 -*-

from __future__ import division

import random

import math

__author__ = "kissg"
__date__ = "2017-03-29"


__mutation_bar__ = [
    "mut_none_bar",
    "mut_reverse_bar",
    "mut_rotate_right_bar",
    "mut_invert_pitch_bar",
    "mut_ascend_pitch_bar",
    "mut_transpose_bar",
    # "mut_regenerate_bar",
    "mut_descend_pitch_bar"
]


def mutate_bar(individual):
    mutation_method = __mutation_bar__
    func = getattr(MutationBar, random.choice(mutation_method))
    func(individual)
    return individual,


class MutationBar(object):
    @classmethod
    def mut_none_bar(cls, ind_bar):
        """
        :return: bar individual itself
        """
        return ind_bar

    # @classmethod
    # def mut_regenerate_bar(cls, ind_bar):
    #     rest = 1
    #     print(id(ind_bar))
    #     print(ind_bar)
    #     for i in range(len(ind_bar)):
    #         pitch = gen.get_pitch()
    #         duration = gen.get_duration([
    #             dt for dt in range(int(math.ceil(1 / rest)), 33, 1)
    #             if dt in gen.DURATION_RANGE
    #         ])
    #         ind_bar[i] = pitch + duration / 100.0
    #         rest -= 1 / duration
    #         if rest == 0.0:
    #             if i < len(ind_bar) - 1:
    #                 for j in range(len(ind_bar) - 1 - i):
    #                     ind_bar.pop()
    #             break
    #     else:
    #         while rest:
    #             pitch = gen.get_pitch()
    #             duration = gen.get_duration([
    #                 dt for dt in range(int(math.ceil(1 / rest)), 33, 1)
    #                 if dt in gen.DURATION_RANGE
    #             ])
    #             ind_bar.append(pitch + duration / 100.0)
    #             rest -= 1 / duration
    #
    #     return ind_bar

    @classmethod
    def mut_reverse_bar(cls, ind_bar):
        """
        :return: reversed bar individual
        """
        ind_bar.reverse()
        return ind_bar

    @classmethod
    def mut_rotate_right_bar(cls, ind_bar):
        """
        :return:
        """
        # todo: should make n a parameter?
        # randint - including both end points.
        n = random.randint(0, len(ind_bar) - 1)
        ls = ind_bar[-n:] + ind_bar[:-n]
        for i, ele in enumerate(ls):
            ind_bar[i] = ele

        return ind_bar

    @classmethod
    def mut_invert_pitch_bar(cls, ind_bar):
        """
        :return: 音程转位
        """
        durations, pitchs = zip(*[math.modf(note) for note in ind_bar])
        octaves, names = zip(*[divmod(int(pitch), 12) for pitch in pitchs])
        names = [12 - n for n in names]  # 音名的转位

        # Notice - ind_bar is a instance of array.array
        for i, pd in enumerate(zip(octaves, names, durations)):
            ind_bar[i] = pd[0] * 12 + pd[1] + pd[2]

        return ind_bar

    @classmethod
    def mut_ascend_pitch_bar(cls, ind_bar):
        """
        :return:
        """
        asc_sorted = sorted(ind_bar, key=lambda t: int(t))
        for i, ele in enumerate(asc_sorted):
            ind_bar[i] = ele
        return ind_bar

    @classmethod
    def mut_descend_pitch_bar(cls, ind_bar):
        """
        :return:
        """
        desc_sorted = sorted(ind_bar, key=lambda t: int(t), reverse=True)
        for i, ele in enumerate(desc_sorted):
            ind_bar[i] = ele
        return ind_bar

    @classmethod
    def mut_transpose_bar(cls, ind_bar):
        """
        :return:
        """
        n = random.randint(1, 4)  # randint - including both end points.

        durations, pitchs = zip(*[math.modf(note) for note in ind_bar])
        ls = [p + n + d if p + n < 97 else 192 - p - n + d for p, d in
              zip(pitchs, durations)]

        for i, ele in enumerate(ls):
            ind_bar[i] = ele

        # return array.array("d", ls),
        return ind_bar

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


__all__ = ["mutate_bar"]
