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

if __name__ == '__main__':
    print(get_geometric_progression_of_2(2, 32))
    print(get_geometric_progression_with_length(1, 2, 10))