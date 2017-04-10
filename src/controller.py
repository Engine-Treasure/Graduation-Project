
__author__ = "Engine"
__date__ = "2017-04-08"


import os
import sys
import tty
import time
from mingus.containers.note import Note, NoteFormatError from mingus.midi import fluidsynth


# initial fluidsynth
fluidsynth.init(
    os.path.join(os.path.dirname(__file__), "statics", "soundfonts", "JR_elepiano.sf2"),
    "alsa")


keymap = {
    "s": "C",
    "e": "C#",
    "d": "D",
    "r": "D#",
    "f": "E",
    "j": "F",
    "i": "F#",
    "k": "G",
    "o": "G#",
    "l": "C",
    "a": "octave up",
    ";": "octave down",

}


if __name__ == "__main__":
    # suppose, 120 bpm
    tty.setraw(sys.stdin.fileno())


    while True:
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            break
        try:
            fluidsynth.play_Note(Note(ch.upper()))
        except NoteFormatError:
            pass

