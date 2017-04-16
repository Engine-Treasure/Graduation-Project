# -*- coding: utf-8 -*-

import os
import json
import time

import fire
import click
from mingus.containers.note import NoteFormatError, Note

from gamc import evolver, txtimg
from mingus.midi import fluidsynth

__author__ = "kissg"
__date__ = "2017-04-13"


def play(func):
    def wrapper(*args, **kwargs):
        bars, log = func(*args, **kwargs)
        print("Oh")
        try:
            for bar in bars:
                fluidsynth.play_Bar(bar)
        except KeyboardInterrupt:
            raise
    return wrapper


def time2duration(t, standard_beat=2):
    if t < 0.046875:
        result = standard_beat / 0.03125
    elif t < 0.09375:
        result = standard_beat / 0.0625
    elif t < 0.1875:
        result = standard_beat / 0.125
    elif t < 0.375:
        result =  standard_beat / 0.25
    elif t < 0.75:
        result = standard_beat / 0.5
    elif t < 1.5:
        result = standard_beat / 1
    elif t < 3:
        result = standard_beat / 2
    elif t < 6:
        result = standard_beat / 4
    else:
        result = standard_beat / 8

    if 1 <= result <= 32:
        return result
    else:
        return 1.0 if result < 1 else 32.0


class Controller(object):

    def __init__(self, soundfont="JR_elepiano", km_file="./gamc/statics/keymap.json", octave=4, meter="4/4", bpm=120):
        # initial fluidsynth
        sf2 = os.path.join("gamc", "statics", "soundfonts",
                           soundfont if soundfont.endswith(".sf2") else soundfont + ".sf2")
        fluidsynth.init(sf2=sf2, driver="alsa")

        # set key map
        with open(km_file) as f:
            self.KEYMAP = json.load(f)

        self.OCTAVE = octave  # init octave

        basic_beat = int(meter.split("/")[-1])  # Get baisc beat from meter
        self.STANDARD_DURATION = basic_beat * 60 / bpm

    @play
    def generate(self):
         return evolver.evolve_from_none()

    @play
    def imitate(self, abc_file):
        return evolver.evolve_from_abc(abc_file)

    @play
    def interacte(self):
        notes = []
        durations = []

        t = 0
        while True:
            key = click.getchar()
            if key == "\x1b":
                break
            elif key == "\r":
                durations.append(
                    time2duration(time.time() - t, self.STANDARD_DURATION))
                evolved_pop, log = evolver.evolve_from_keyboard(notes, durations)
                play_bars(evolved_pop)
                probabilities = count(notes, durations)
                del notes[:]
                del durations[:]
                t = 0

            elif key in "a;":
                if key == "a":
                    self.OCTAVE = OCTAVE - 1 if OCTAVE < 8 else OCTAVE
                    print(txtimg[OCTAVE])
                else:
                    self.OCTAVE = OCTAVE + 1 if OCTAVE > 0 else OCTAVE
                    print(txtimg[OCTAVE])
            elif key in "012345678":
                self.OCTAVE = int(key)
                print(txtimg[OCTAVE])
            elif key in "sdfhjkleruio":
                if self.KEYMAP.get(key):
                    notes.append(
                        Note("-".join(map(str, [self.KEYMAP.get(key), self.OCTAVE]))))
                if t:
                    durations.append(
                        time2duration(time.time() - t, self.STANDARD_DURATION))
                    t = time.time()
                elif not t:
                    t = time.time()
                try:
                    fluidsynth.play_Note(notes[-1])
                except (KeyError, NoteFormatError):
                    pass



if __name__ == '__main__':
    fire.Fire(Controller)