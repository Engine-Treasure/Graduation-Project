# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-29"

import random

from mingus.containers import Note, Bar

from src.util import remove_at


def cxOnePoint(ind1, ind2):
    size = min(len(ind1), len(ind2))
    cxpoint = random.randint(1, size - 1)

    cx1, cx2 = [(_[2][0], _[1]) for _ in ind1[cxpoint:]], \
               [(_[2][0], _[1]) for _ in ind2[cxpoint:]]
    ind1, ind2 = remove_at(ind1, cxpoint), remove_at(ind2, cxpoint)

    for note, duration in cx2:
        # 若 bar 的剩余时值不足, 将跳过当前 note
        ind1.place_notes(Note(note), duration)
    for note, duration in cx1:
        ind2.place_notes(Note(note), duration)

    if not ind1.is_full():
        ind1.place_rest(ind1.value_left())
    if not ind2.is_full():
        ind2.place_rest(ind2.value_left())

    return ind1, ind2


if __name__ == '__main__':
    pass
