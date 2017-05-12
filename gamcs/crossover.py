# -*- coding: utf-8 -*-

import random

import math

__author__ = "kissg"
__date__ = "2017-03-29"


def cx_one_point_bar(ind_1, ind_2):
    """
    In order to make sure the two offsprings are complete.
    There is limit to the cross point.
    Like DEAP's crossover operator, modify inplace.
    """

    # 为保证交叉之后, 两个个体都是完整的小节,
    durations_1, pitchs_1 = zip(*[math.modf(note) for note in ind_1])
    durations_2, pitchs_2 = zip(*[math.modf(note) for note in ind_2])
    time_1 = [1 / round(duration * 100) for duration in durations_1]
    time_2 = [1 / round(duration * 100) for duration in durations_2]

    # cumulative time
    ctime_1 = [sum(time_1[:i + 1]) for i, t in enumerate(time_1)]
    ctime_2 = [sum(time_2[:i + 1]) for i, t in enumerate(time_2)]

    atime = [t for t in ctime_1 if t in ctime_2]

    if not atime or atime == [1.0]:  # 没有重合的部分
        return ind_1, ind_2
    else:
        chosen_pos = random.choice(atime)
        # 相同索引所在位置的元素应保留在原序列中
        pos_1, pos_2 = ctime_1.index(chosen_pos) + 1, \
            ctime_2.index(chosen_pos) + 1
        tmp_1, tmp_2 = ind_1[:pos_1] + ind_2[pos_2:], \
            ind_2[:pos_2] + ind_1[pos_1:]

        del ind_1[:]
        for i, ele in enumerate(tmp_1):
            ind_1.append(ele)

        del ind_2[:]
        for i, ele in enumerate(tmp_2):
            ind_2.append(ele)

        return ind_1, ind_2


__all__ = ["cx_one_point_bar"]
