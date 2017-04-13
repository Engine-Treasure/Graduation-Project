# -*- coding: utf-8 -*-

from __future__ import division

import json
import os
import time

import click
from mingus.containers.note import Note, NoteFormatError
from mingus.midi import fluidsynth

from common import count
from evolver import evolve_from_keyboard
from txtimg import txtimg

__author__ = "Engine"
__date__ = "2017-04-08"

soundfont = "JR_elepiano.sf2"
meter = "4/4"  # 每小节拍数/几分音符为一拍
bpm = 120
km_file = os.path.join(os.path.dirname(__file__), "statics/keymap.json")

KEYMAP = {}
OCTAVE = None
STANDARD_DURATION = None


def init(soundfont=soundfont, meter=meter, bpm=bpm, km_file=km_file,
         octave=4):
    # initial fluidsynth
    sf2 = os.path.join(os.path.dirname(__file__), "statics", "soundfonts",
        soundfont if soundfont.endswith(".sf2") else soundfont + ".sf2")
    fluidsynth.init(sf2=sf2, driver="alsa")

    global KEYMAP
    with open(km_file) as f:
        KEYMAP = json.load(f)

    global OCTAVE
    OCTAVE = octave

    global STANDARD_DURATION
    basic_beat = int(meter.split("/")[-1])
    STANDARD_DURATION = basic_beat * 60 / bpm


def play_bars(bars):
    try:
        for bar in bars:
            fluidsynth.play_Bar(bar)
    except KeyboardInterrupt:
        pass


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


def start():
    # suppose, 120 bpm
    init()
    # raw_input("Press any key to start...")  # waiting for any key press

    notes = []
    durations = []

    global OCTAVE

    t = 0
    while True:
        key = click.getchar()
        if key == "\x1b":
            break
        elif key == "\r":
            durations.append(
                time2duration(time.time() - t, STANDARD_DURATION))
            evolved_pop, log = evolve_from_keyboard(notes, durations)
            play_bars(evolved_pop)
            probabilities = count(notes, durations)
            del notes[:]
            del durations[:]
            t = 0

        elif key in "a;":
            if key == "a":
                OCTAVE = OCTAVE - 1 if OCTAVE < 8 else OCTAVE
                print(txtimg[OCTAVE])
            else:
                OCTAVE = OCTAVE + 1 if OCTAVE > 0 else OCTAVE
                print(txtimg[OCTAVE])
        elif key in "012345678":
            OCTAVE = int(key)
            print(txtimg[OCTAVE])
        elif key in "sdfhjkleruio":
            if KEYMAP.get(key):
                notes.append(
                    Note("-".join(map(str, [KEYMAP.get(key), OCTAVE]))))
            if t:
                durations.append(
                    time2duration(time.time() - t, STANDARD_DURATION))
                t = time.time()
            elif not t:
                t = time.time()
            try:
                fluidsynth.play_Note(notes[-1])
            except (KeyError, NoteFormatError):
                pass

if __name__ == "__main__":
    start()


