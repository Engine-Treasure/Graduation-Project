# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-20"


def get_geometric_progression_of_2(start, stop):
    """
    The usage is just like range(start, stop),
    Because my range won't be large, I just use `range()` and `filter()` ,
    instead of the the blow one: multiply and power.
    :param start:
    :param stop:
    :param a:
    :return:
    """
    return filter(lambda x: not (x - 1) & x, range(start, stop + 1))


def get_geometric_progression_with_length(start, a, length):
    return [start * a ** (n - 1) for n in range(1, length + 1)]


def get_names_octaves_durations(bar):
    """
    Return a tuple lists: note names, octaves, durations
    """
    _, durations, notes = zip(*bar)
    names, octaves = zip(*((no[0].name, no[0].octave) for no in notes))

    return names, octaves, durations


def get_combination_order2(seq_obj):
    ps = seq_obj[:-1]
    ns = seq_obj[1:]
    return [(p, n) for p, n in zip(ps, ns)]


def is_monotone(L):
    print(L)
    return strictly_decreasing(L) and strictly_decreasing(L)


def strictly_increasing(L):
    return all(x < y for x, y in zip(L, L[1:]))


def strictly_decreasing(L):
    return all(x > y for x, y in zip(L, L[1:]))


def non_increasing(L):
    return all(x >= y for x, y in zip(L, L[1:]))


def non_decreasing(L):
    return all(x <= y for x, y in zip(L, L[1:]))


def remove_at(bar, pos):
    """Remove the NoteContainer after pos in the Bar."""
    for i in range(len(bar) - pos):
        bar.remove_last_entry()
    return bar


if __name__ == '__main__':
    print(get_geometric_progression_of_2(2, 32))
    print(get_geometric_progression_with_length(1, 2, 10))
