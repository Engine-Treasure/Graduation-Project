# -*- coding: utf-8 -*-

import fire

__author__ = "kissg"
__date__ = "2017-04-13"

from gamc import evolver
from mingus.midi import fluidsynth


def init():
    pass


def play(func):
    def wrapper(self, *args, **kwargs):
        bars, log = func(*args, **kwargs)
        try:
            for bar in bars:
                fluidsynth.play_Bar(bar)
        except KeyboardInterrupt:
            pass
    return wrapper


class Controller(object):

    @play
    def generate(self):
        evolver.evolve_from_none()

    def imitate(self):
        pass

    def interacte(self):
        pass


if __name__ == '__main__':
   fire.Fire(Controller)