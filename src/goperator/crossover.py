# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-29"

from math import ceil

import random

from mingus.containers import Note, Bar
from deap import tools

from src.common import remove_at
from src.gen import gen_pitch, gen_duration


def cross_bar(ind1, ind2, ppb=None, dpb=None):
    func = getattr(BarCrossover, random.choice(__method__))
    ind1, ind2 = func(ind1, ind2)

    if not ind1.is_full():
        if random.random() < 0.05:
            ind1.place_rest(ind1.value_left())
        else:
            while not ind1.is_full():
                # todo - place rest
                ind1.place_notes(gen_pitch(p=ppb),
                                 gen_duration(_max=int(ceil(ind1.value_left())),
                                              p=dpb))

    if not ind2.is_full():
        if random.random() < 0.05:
            ind2.place_rest(ind2.value_left())
        else:
            while not ind2.is_full():
                # todo - place rest
                ind2.place_notes(gen_pitch(p=ppb),
                                 gen_duration(_max=int(ceil(ind2.value_left())),
                                              p=dpb))

    return ind1, ind2


def cross_sentence(ind1, ind2):
    """交叉会改变乐句包含的小节数啊"""
    func = getattr(tools, random.choice(__method__))
    ind1, ind2 = func(ind1, ind2) if func != tools.cxUniform \
        else func(ind1, ind2, 0.5)
    if len(ind1) != len(ind2):
        if len(ind1) < len(ind2):
            ind1, ind2 = ind2, ind1
        while len(ind1) != 4:
            # make sure the two individuals have the same length
            ind2.append(ind1.pop())

    return ind1, ind2


class BarCrossover(object):
    @classmethod
    def cxOnePoint(cls, ind1, ind2, ppd=None, dpb=None):
        size = min(len(ind1), len(ind2))
        cxpoint = random.randint(1, size)

        cx1, cx2 = list(ind1[cxpoint:]), list(ind2[cxpoint:])
        ind1, ind2 = remove_at(ind1, cxpoint), remove_at(ind2, cxpoint)

        for note in cx2:
            # 若 bar 的剩余时值不足, 将跳过当前 note
            if note[2]:
                ind1.place_notes(Note(note[2][0]), note[1])
        for note in cx1:
            if note[2]:
                ind2.place_notes(Note(note[2][0]), note[1])

        return ind1, ind2

    @classmethod
    def cxTwoPoint(cls, ind1, ind2, ppd=None, dpb=None):
        size = min(len(ind1), len(ind2))
        cxpoint1 = random.randint(1, size)
        try:
            cxpoint2 = random.randint(1, size - 1)
        except ValueError:
            # 可能的一场是遇到单个音符的小节, size=1
            # 直接选择交换两个个体
            return ind2, ind1

        if cxpoint2 >= cxpoint1:
            cxpoint2 += 1
        else:
            cxpoint1, cxpoint2 = cxpoint2, cxpoint1

        # cx1, cx2 分别是两个个体要交换的片段
        cx1, cx2 = list(ind1[cxpoint1:cxpoint2]), list(ind2[cxpoint1:cxpoint2])
        r1, r2 = list(ind1[cxpoint2:]), list(ind2[cxpoint2:])
        # 从前一个交换点开始, 两个个体都要删除后续的音
        ind1, ind2 = remove_at(ind1, cxpoint1), remove_at(ind2, cxpoint1)

        for note in cx2:
            if note[2]:  # not None
                ind1.place_notes(Note(note[2][0]), note[1])
        for note in r1:
            if note[2]:  # not None
                ind1.place_notes(Note(note[2][0]), note[1])

        for note in cx1:
            if note[2]:
                ind2.place_notes(Note(note[2][0]), note[1])
        for note in r2:
            if note[2]:
                ind2.place_notes(Note(note[2][0]), note[1])

        return ind1, ind2

    @classmethod
    def cxMessyOnePoint(cls, ind1, ind2, ppd=None, dpb=None):

        cxpoint1 = random.randint(0, len(ind1))
        cxpoint2 = random.randint(0, len(ind2))

        cx1, cx2 = list(ind1[cxpoint1:]), list(ind2[cxpoint2:])
        ind1, ind2 = remove_at(ind1, cxpoint2), remove_at(ind2, cxpoint1)

        for note in cx2:
            # 若 bar 的剩余时值不足, 将跳过当前 note
            if note[2]:
                ind1.place_notes(Note(note[2][0]), note[1])
        for note in cx1:
            if note[2]:
                ind2.place_notes(Note(note[2][0]), note[1])

        return ind1, ind2

    @classmethod
    def cxUniform(cls, ind1, ind2, indpb=0.5, ppd=None, dpb=None):
        """交换某位音名"""
        size = min(len(ind1), len(ind2))
        for i in xrange(size):
            if random.random() < indpb:
                ind1[i][2], ind2[i][2] = ind2[i][2], ind1[i][2]
        return ind1, ind2

    @classmethod
    def cxBlend(cls, ind1, ind2, ppd=None, dpb=None):
        pass


__method__ = ["cxUniform"] # , "cxMessyOnePoint", "cxOnePoint", "cxTwoPoint"]
__all__ = ["cross_bar", "cross_sentence"]
