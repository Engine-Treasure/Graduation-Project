# -*- coding: utf-8 -*-

import json
import os
import time
import math
import webbrowser
from copy import deepcopy

import click
import fire
import numpy as np
import matplotlib.pyplot as plt
import mingus.extra.lilypond as lp
from deap import creator
from mingus.containers.note import NoteFormatError, Note
from mingus.containers.note_container import NoteContainer
from mingus.containers.bar import Bar
from mingus.containers.track import Track
from mingus.containers.composition import Composition
from mingus.midi import fluidsynth, midi_file_out

from gamc import evolver, txtimg, abcparse, common

__author__ = "kissg"
__date__ = "2017-04-13"


def play(func):
    """decorator - for playing music after evolving"""

    def wrapper(*args, **kwargs):
        bars, log = func(*args, **kwargs)
        track = Track()

        print("Listening ...")
        try:
            for bar in bars:
                track.add_bar(bar)
        except KeyboardInterrupt:
            raise

        lp.to_pdf(lp.from_Track(track), "out.pdf")
        webbrowser.open("out.pdf.pdf")
        midi_file_out.write_Track("out.mid", track)

        fig = plt.figure()

        plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)

        headers = ["avg", "std", "min", "max"]
        for rank, header in enumerate(headers):
            plt.scatter(np.arange(len(log.select(header))),
                        np.sum(np.array(log.select(header)) / 8, axis=1))

        fig.savefig("out.png")
        webbrowser.open_new("out.png")

        fluidsynth.play_Track(track)

    return wrapper


def play_back(bars):
    track = Track()
    for bar in bars:
        track.add_bar(bar)

    lp.to_pdf(lp.from_Track(track), "tmp.pdf")
    midi_file_out.write_Track("tmp.mid", track)
    webbrowser.open("tmp.pdf.pdf")
    fluidsynth.play_Track(track)


def time2duration(t, standard_beat=2):
    if t < 0.046875:
        result = standard_beat / 0.03125
    elif t < 0.09375:
        result = standard_beat / 0.0625
    elif t < 0.1875:
        result = standard_beat / 0.125
    elif t < 0.375:
        result = standard_beat / 0.25
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
    def __init__(self, soundfont="JR_elepiano",
                 km_file="./gamc/statics/keymap.json", octave=4, meter="4/4",
                 bpm=120):
        # initial fluidsynth
        sf2 = os.path.join("gamc", "statics", "soundfonts",
                           soundfont if soundfont.endswith(
                               ".sf2") else soundfont + ".sf2")
        fluidsynth.init(sf2=sf2, driver="alsa")

        # set key map
        with open(km_file) as f:
            self.KEYMAP = json.load(f)

        self.OCTAVE = octave  # init octave

        basic_beat = int(meter.split("/")[-1])  # Get baisc beat from meter
        self.STANDARD_DURATION = basic_beat * 60 / bpm

    def play_abc(self, abc_file):
        key, meter, notes = abcparse.parse_abc(abc_file)
        names, durations = zip(*
            [(note[0].rstrip("*").upper(), int(note[1])) for note in notes])
        names = [[name[:-1], int(name[-1])] for name in names]

        track = Track()
        for name, duration in zip(names, durations):
            print(name, duration)
            track.add_notes(Note(*name), duration=duration)

        lp.to_pdf(lp.from_Track(track), "tmp.pdf")
        midi_file_out.write_Track("tmp.mid", track)
        webbrowser.open_new("tmp.pdf.pdf")

        fluidsynth.play_Track(track)

    def generate(self, ngen=100, mu=100, cxpb=0.9, mutpb=0.1):

        pop, log = evolver.evolve_bar(ngen=ngen, mu=mu, cxpb=cxpb, mutpb=mutpb)
        print(len(set(pop)))

        track = Track()
        for ind in pop:
            durations, pitchs = zip(*[math.modf(note) for note in ind])
            notes = [Note().from_int(int(pitch)) for pitch in pitchs]
            durations = [int(round(duration * 100)) for duration in durations]
            bar = Bar()
            for note, duration in zip(notes, durations):
                bar.place_notes(note, duration)
            track.add_bar(bar)

        lp.to_pdf(lp.from_Track(track), "tmp.pdf")
        midi_file_out.write_Track("tmp.mid", track)
        webbrowser.open("tmp.pdf.pdf")
        fig = plt.figure()

        plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)

        headers = ["avg", "std", "min", "max"]
        for rank, header in enumerate(headers):
            plt.scatter(np.arange(len(log.select(header))),
                        np.sum(np.array(log.select(header)) / 8, axis=1))

        fig.savefig("out.png")
        webbrowser.open_new("out.png")
        fluidsynth.play_Track(track)

        # bars = [Bar(Note().from_int(int(pitch)), int(round(duration * 100))) for pitch, duration in zip(pitchs, durations)]

        print(log)

    def imitate(self, abc_file, ngen=100, mu=100, cxpb=0.9, mutpb=0.1):
        pop, log = evolver.evolve_from_abc(abc_file, ngen=ngen, mu=mu,
                                           cxpb=cxpb,
                                           mutpb=mutpb)
        print(pop)
        print(set(pop))
        print(len(set(pop)))

        track = Track()
        for ind in pop:
            durations, pitchs = zip(*[math.modf(note) for note in ind])
            notes = [Note().from_int(int(pitch)) for pitch in pitchs]
            durations = [int(round(duration * 100)) for duration in durations]
            bar = Bar()
            for note, duration in zip(notes, durations):
                bar.place_notes(note, duration)
            track.add_bar(bar)

        lp.to_pdf(lp.from_Track(track), "tmp.pdf")
        midi_file_out.write_Track("tmp.mid", track)
        webbrowser.open("tmp.pdf.pdf")
        fig = plt.figure()

        plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)

        headers = ["avg", "std", "min", "max"]
        for rank, header in enumerate(headers):
            plt.scatter(np.arange(len(log.select(header))),
                        np.sum(np.array(log.select(header)) / 8, axis=1))

        fig.savefig("out.png")
        webbrowser.open_new("out.png")
        fluidsynth.play_Track(track)

        # bars = [Bar(Note().from_int(int(pitch)), int(round(duration * 100))) for pitch, duration in zip(pitchs, durations)]

        print(log)

    def interact(self, ngen=100, mu=100, cxpb=0.9, mutpb=0.1):
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
                try:
                    bars, log = evolver.evolve_from_keyboard(notes, durations,
                                                             ngen=ngen, mu=mu,
                                                             cxpb=cxpb,
                                                             mutpb=mutpb)
                    play_back(bars)

                except KeyboardInterrupt:
                    pass

                finally:  # reset notes, durations and t
                    del notes[:]
                    del durations[:]
                    t = 0
            elif key in self.KEYMAP:
                v = self.KEYMAP.get(key)
                if v in ("OD", "OU"):  # octave down and octave up
                    if v == "OD":
                        self.OCTAVE = self.OCTAVE - 1 \
                            if self.OCTAVE < 8 else self.OCTAVE
                        print(txtimg.txtimg[self.OCTAVE])
                    else:
                        self.OCTAVE = self.OCTAVE + 1 \
                            if self.OCTAVE > 0 else self.OCTAVE
                        print(txtimg.txtimg[self.OCTAVE])
                elif v in (0, 1, 2, 3, 4, 5, 6, 7, 8):
                    self.OCTAVE = int(key)
                    print(txtimg.txtimg[self.OCTAVE])
                elif v in ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A",
                           "A#", "B"):
                    # v is a unicode instance
                    notes.append(Note("-".join(map(str, [v, self.OCTAVE]))))
                    if t:
                        durations.append(time2duration(time.time() - t,
                                                       self.STANDARD_DURATION))
                        t = time.time()
                    elif not t:  # start timing, t=0, no duration is recorded
                        t = time.time()
                    try:
                        fluidsynth.play_Note(notes[-1])
                    except NoteFormatError:
                        pass
                else:
                    raise KeyError
            else:
                pass


if __name__ == '__main__':
    fire.Fire(Controller)
