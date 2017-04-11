# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-04-11"


from copy import deepcopy
from collections import Counter

from mingus.containers import Bar


def construct_bars(notes, durations, container=Bar):
    """
    :param notes: sequences of notes
    :param durations: sequences of durations
    :param container: mingus.containers.Bar or creator.Bar
    :return: list of bars
    """
    bars = []
    bar = container()
    for note, duration in zip(notes, durations):
        print(note, duration)

        if bar.is_full():
            bars.append(deepcopy(bar))
            bar = container()
            bar.place_notes(notes=note, duration=duration)
        else:
            # add new note to bar
            if bar.place_notes(notes=note, duration=duration):
                continue
            else:  # fail, because the new note is long than remainder of bar
                bar.place_rest(bar.value_left())
                bars.append(deepcopy(bar))  # complete current bar
                bar = container()  # create new bar
                bar.place_notes(notes=note, duration=duration)

    # run out of notes and durations, but the current bar is not full
    if not bar.is_full():
        bar.place_rest(bar.value_left())
    bars.append(deepcopy(bar))

    return bars


def count(notes, durations):
    print(notes)
    print(Counter(notes))
    print(Counter(durations))
    return {
        "note": Counter(notes),
        "duration": Counter(durations)
    }



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


