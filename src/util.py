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
    names, octaves = zip(
        *((no[0].name, no[0].octave) for no in notes if no is not None))
    return names, octaves, durations


def get_combination_order2(seq_obj):
    return [(p, n) for p, n in zip(seq_obj[:-1], seq_obj[1:])]


def is_monotone(L):
    """单调"""
    return non_increasing(L) or non_decreasing(L)


def strictly_increasing(L):
    """严格单调递增"""
    # None as 0
    return all(x < y for x, y in zip(L[:-1], L[1:]))


def strictly_decreasing(L):
    """严格单调递减"""
    return all(x > y for x, y in zip(L[:-1], L[1:]))


def non_increasing(L):
    """非严格单调递减"""
    return all(x >= y for x, y in zip(L[:-1], L[1:]))


def non_decreasing(L):
    """非严格单调递增"""
    return all(x <= y for x, y in zip(L[:-1], L[1:]))


def remove_at(bar, pos):
    """Remove the NoteContainer after pos in the Bar."""
    for i in range(len(bar) - pos):
        bar.remove_last_entry()
    return bar


if __name__ == '__main__':
    print(get_geometric_progression_of_2(2, 32))
    print(get_geometric_progression_with_length(1, 2, 10))
