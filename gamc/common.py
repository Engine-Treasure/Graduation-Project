# -*- coding: utf-8 -*-

from __future__ import division

import math
from copy import deepcopy
from collections import Counter, OrderedDict

from mingus.containers import Bar, Note
from deap import creator

from util import get_geometric_progression_of_2

__author__ = "kissg"
__date__ = "2017-04-11"

PITCH_PROBABILITY = None

name2int = {
    "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
    "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11
}


def init_pop_from_seq(seq):
    ls = []
    rest = 1.0
    bar = creator.Bar()
    for i in seq:
        if rest - i[1] > 0.0:
            bar.append(i[0])
            rest -= i[1]
        elif rest - i[1] == 0.0:
            bar.append(i[0])
            ls.append(deepcopy(bar))
            bar = creator.Bar()
            rest = 1.0
        else:
            last_note = bar.pop()
            rest = 1.0 - sum(1.0 / math.modf(note)[0] for note in bar)
            bar.append(int(last_note) + 1.0 / rest / 100)
            ls.append(deepcopy(bar))
            bar = creator.Bar()
            bar.append(i[0])
            rest = 1.0 - i[1] if i[1] != 1.0 else 1.0
    if rest != 1.0:
        ls.append(deepcopy(bar))
    return ls


def construct_bars(names, durations, container=Bar):
    """
    :param notes: sequences of notes
    :param durations: sequences of durations
    :param container: mingus.containers.Bar or creator.Bar
    :return: list of bars
    """
    bars = []
    bar = container()
    for name, duration in zip(names, durations):
        # print(name, duration)

        if bar.is_full():
            bars.append(deepcopy(bar))
            bar = container()
            bar.place_notes(notes=name, duration=duration)
        else:
            # add new note to bar
            if bar.place_notes(notes=name, duration=duration):
                continue
            else:  # fail, because the new note is long than remainder of bar
                bar.place_rest(bar.value_left())
                bars.append(deepcopy(bar))  # complete current bar
                bar = container()  # create new bar
                bar.place_notes(notes=name, duration=duration)

    # run out of notes and durations, but the current bar is not full
    if not bar.is_full():
        bar.place_rest(bar.value_left())
    bars.append(deepcopy(bar))

    return bars


def count(notes, durations):
    """
    :param notes: list of notes, a note is a Note instance or a str of note name
    :param durations: list of durations
    :return: return a tuple of pitch_probabilities and duration_probabilities
    """
    # note name to pitch
    if isinstance(notes[0], str):
        names, octaves = zip(*(note.split("-") for note in notes))
        pitchs = [
            int(octave) * 12 + name2int[name] for name, octave in zip(names, octaves)
            ]
    elif isinstance(notes[0], Note):
        pitchs = [note.octave * 12 + name2int[note.name] for note in notes]
    else:
        raise TypeError

    durations = [int(d) for d in durations]

    pitchs = filter(lambda x: x in range(1, 97), pitchs)
    durations = filter(lambda x: x in get_geometric_progression_of_2(1, 32), durations)

    pitch_counter = Counter(pitchs)
    # print(pitch_counter)
    duration_counter = Counter(durations)
    # print(duration_counter)

    pitch_total = len(pitchs)
    duration_total = len(durations)

    pitch_probability = OrderedDict(
        sorted({k: v / pitch_total for k, v in
                pitch_counter.iteritems()}.iteritems(), key=lambda t: t[0]))
    duration_probability = OrderedDict(
        sorted({k: v / duration_total for k, v in
                duration_counter.iteritems()}.iteritems(), key=lambda t: t[0]))

    pitch_probability_list = [
        pitch_probability[k] if k in pitch_counter else 0 for k in xrange(9, 97)
        ]

    duration_probability_list = [
        duration_probability[k] if k in duration_counter else 0
        for k in get_geometric_progression_of_2(1, 32)
        ]
    # print(duration_probability_list)

    return pitch_probability_list, duration_probability_list


def remove_at(bar, pos):
    """Remove the NoteContainer after pos in the Bar."""
    for i in range(len(bar) - pos):
        bar.remove_last_entry()
    return bar


def get_names_octaves_durations(bar):
    """
    Return a tuple lists: note names, octaves, durations
    """
    _, durations, notes = zip(*bar)
    names, octaves = zip(
        *((no[0].name, no[0].octave) for no in notes if no is not None))
    return names, octaves, durations



