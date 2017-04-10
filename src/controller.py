# -*- coding: utf-8 -*-

from __future__ import division

import os
import sys
import tty
import json
import time
from mingus.containers.note import Note, NoteFormatError
from mingus.midi import fluidsynth

from txtimg import txtimg

__author__ = "Engine"
__date__ = "2017-04-08"

soundfont = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
meter = "4/4"  # 每小节拍数/几分音符为一拍
bpm = 120
km_file = "src/statics/keymap.json"

KEYMAP = {}
OCTAVE = None
STANDARD_DURATION = None


def init(soundfont=soundfont, meter=meter, bpm=bpm, km_file=km_file,
         octave=4):
    # initial fluidsynth
    fluidsynth.init(sf2="/usr/share/sounds/sf2/FluidR3_GM.sf2", driver="alsa")

    global KEYMAP
    with open(km_file) as f:
        KEYMAP = json.load(f)

    global OCTAVE
    OCTAVE = octave

    global STANDARD_DURATION
    basic_beat = int(meter.split("/")[-1])
    STANDARD_DURATION = basic_beat * 60 / bpm


def play():
    pass


# initial fluidsynth
# fluidsynth.init(sf2="/usr/share/sounds/sf2/FluidR3_GM.sf2", driver="alsa")
# fluidsynth.init(
#     os.path.join(os.path.dirname(__file__), "statics", "soundfonts", "JR_elepiano.sf2"),
#     "alsa")


def time2duration(t, standard_beat=2):
    if t < 0.046875:
        return standard_beat / 0.03125
    elif t < 0.09375:
        return standard_beat / 0.0625
    elif t < 0.1875:
        return standard_beat / 0.125
    elif t < 0.375:
        return standard_beat / 0.25
    elif t < 0.75:
        return standard_beat / 0.5
    elif t < 1.5:
        return standard_beat / 1
    elif t < 3:
        return standard_beat / 2
    elif t < 6:
        return standard_beat / 4
    else:
        return standard_beat / 8


if __name__ == "__main__":
    # suppose, 120 bpm
    init()
    # raw_input("Press any key to start...")  # waiting for any key press

    tty.setraw(sys.stdin.fileno())

    notes = []
    durations = []

    t = 0
    while True:
        key = sys.stdin.read(1)
        if key == "\x1b":
            tty.setcbreak(sys.stdin.fileno())
            for note, duration in zip(notes, durations):
                print(note, duration)
            break

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
        else:
            if KEYMAP.get(key):
                notes.append(
                    Note("-".join(map(str, [KEYMAP.get(key), OCTAVE]))))
            if t:
                durations.append(
                    time2duration(time.time() - t, STANDARD_DURATION))
                t = time.time()
            try:
                fluidsynth.play_Note(notes[-1])
            except (KeyError, NoteFormatError):
                pass


