# -*- coding: utf-8 -*-

from __future__ import division

import json
import math
import os
import random
import time
import webbrowser

import click
import fire
import matplotlib.pyplot as plt
import mingus.extra.lilypond as lp
import numpy as np
from mingus.containers.note import NoteFormatError, Note
from mingus.containers.track import Track
from mingus.midi import fluidsynth, midi_file_out

from gamcs import evolver, txtimg, abcparse, gen, cal

__author__ = "kissg"
__date__ = "2017-04-13"

name2int = {
    "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
    "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11
}


# def play(func):
#     """decorator - for playing music after evolving"""
#
#     def wrapper(*args, **kwargs):
#         bars, log = func(*args, **kwargs)
#         track = Track()
#
#         print("Listening ...")
#         try:
#             for bar in bars:
#                 track.add_bar(bar)
#         except KeyboardInterrupt:
#             raise
#
#         lp.to_pdf(lp.from_Track(track), "out.pdf")
#         webbrowser.open("out.pdf.pdf")
#         midi_file_out.write_Track("out.mid", track)
#
#         if log:
#
#             fig = plt.figure()
#
#             plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
#
#             headers = ["avg", "std", "min", "max"]
#             for rank, header in enumerate(headers):
#                 plt.scatter(np.arange(len(log.select(header))),
#                             np.sum(np.array(log.select(header)) / 8, axis=1))
#
#             fig.savefig("out.png")
#             webbrowser.open_new("out.png")
#
#         fluidsynth.play_Track(track)
#
#     return wrapper


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


def compose(pop, mu, selected=None):
    df = cal.cal_bar_similarity(pop)  # 计算各小节间的两两匹配程度

    # 若给定 selected, 则其为乐曲的第一个小节, 否则随机选择
    composition = [selected if selected else random.choice(pop)]
    for i in range(mu):
        idx = pop.index(composition[-1])
        # 从相似度最高的 5 个小节中选择一个, 获取其索引
        nearest5 = df[idx].nlargest(5)
        choice = nearest5.sample(1).keys()[0]
        while pop[choice] in composition[-4:]:
            nearest5.pop(choice)
            choice = nearest5.sample(1).keys()[0]
        composition.append(pop[choice])
        # composition = pop

    return composition


def after_composing(track, fn="out"):
    lp.to_pdf(lp.from_Track(track), fn if fn.endswith(".pdf") else fn + ".pdf")
    midi_file_out.write_Track(fn if fn.endswith(".mid") else fn + ".mid", track)


def visualize_log(log, fn="out"):

    fig = plt.figure()

    headers = ["avg", "max"]
    objective = ["Chord", "Interval", "Duration", "Experience", "Range",
                 "Length", "Change", "Diversity"]

    for i, header in enumerate(headers):
        ax = fig.add_subplot(2, 1, i + 1)
        for g in range(8):
            ax.plot(
                np.arange(len(log.select(header))),
                np.array(log.select(header))[:, g],
                # np.mean(np.array(log.select(header)), axis=1),
                'o-',
                label=objective[g]
            )
        ax.set_xlabel("Generation")
        ax.set_ylabel("Fitness")
        ax.set_title(header, fontsize=18)
        ax.set_ylim(-0.05, 1.05)
        ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))

    plt.tight_layout()
    fig.savefig(fn if fn.endswith(".png") else fn + ".png", bbox_inches="tight")


class Controller(object):
    def __init__(self, soundfont="JR_elepiano",
                 km_file="./gamcs/statics/keymap.json", octave=4, meter="4/4",
                 bpm=120):
        # initial fluidsynth
        sf2 = os.path.join("gamcs", "statics", "soundfonts",
                           soundfont if soundfont.endswith(
                               ".sf2") else soundfont + ".sf2")
        fluidsynth.init(sf2=sf2, driver="alsa")

        # set key map, for interactive playing
        with open(km_file) as f:
            self.KEYMAP = json.load(f)

        self.OCTAVE = octave  # initial octave

        basic_beat = int(meter.split("/")[-1])  # Get baisc beat from meter
        self.STANDARD_DURATION = basic_beat * 60 / bpm

    def play_abc(self, abc_file):
        key, meter, notes = abcparse.parse_abc(abc_file)

        track = Track()
        for note in notes:
            track.add_notes(Note(*note[0]), duration=note[1])

        after_composing(track)

        fluidsynth.play_Track(track)

    def generate(self, ngen=100, mu=100, cxpb=0.9):

        pop, log = evolver.evolve_bar_c(ngen=ngen, mu=mu, cxpb=cxpb)
        print(len(set([i.tostring() for i in pop])) / mu)  # 查看最终小节多样性

        pop = compose(pop, mu)  # 以进化得到的小节谱曲

        durations, pitchs = zip(
            *[math.modf(note) for ind in pop for note in ind])
        notes = [Note().from_int(int(pitch)) for pitch in pitchs]
        durations = [int(round(duration * 100)) for duration in durations]

        track = Track()
        for note, duration in zip(notes, durations):
            track.add_notes(note, duration)

        after_composing(track, fn="generate")

        visualize_log(log, fn="generate")

        fluidsynth.play_Track(track)

    def imitate(self, abc_file, ngen=100, cxpb=0.9):
        key, meter, notes = abcparse.parse_abc(abc_file)

        pitchs, durations = zip(
            *[(note[0][1] * 12 + gen.name2int[note[0][0]], note[1]) for note in
              notes])
        # 为了构造的便利, 第二个元素是时值的倒数
        prepare_pop = [
            (p + d / 100.0, 1.0 / d) for p, d in zip(pitchs, durations)
        ]

        pop = gen.init_pop_from_seq(prepare_pop)
        pop, log = evolver.evolve_bar_nc(pop, ngen=ngen, mu=len(pop), cxpb=cxpb)
        pop = compose(pop, mu=len(pop))
        print(len(set([i.tostring() for i in pop])) / len(pop))  # 查看最终小节多样性

        durations, pitchs = zip(
            *[math.modf(note) for ind in pop for note in ind])
        notes = [Note().from_int(int(pitch)) for pitch in pitchs]
        durations = [int(round(duration * 100)) for duration in durations]

        track = Track()
        for note, duration in zip(notes, durations):
            track.add_notes(note, duration)

        after_composing(track, fn="imitate")

        visualize_log(log, fn="imitate")

        fluidsynth.play_Track(track)

    def interact(self, ngen=100, cxpb=0.9):
        notes = []
        durations = []

        t = 0
        while True:
            key = click.getchar()
            if key == "\x1b":  # Escape 键, 退出程序
                break
            elif key in self.KEYMAP:
                v = self.KEYMAP[key]
                if v in ("OD", "OU"):  # octave down and octave up
                    if v == "OU":
                        self.OCTAVE = self.OCTAVE + 1 \
                            if self.OCTAVE < 8 else self.OCTAVE
                        print(txtimg.txtimg[self.OCTAVE])
                    else:
                        self.OCTAVE = self.OCTAVE - 1 \
                            if self.OCTAVE > 0 else self.OCTAVE
                        print(txtimg.txtimg[self.OCTAVE])
                elif v in (0, 1, 2, 3, 4, 5, 6, 7, 8):
                    self.OCTAVE = int(key)
                    print(txtimg.txtimg[self.OCTAVE])
                elif v in ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A",
                           "A#", "B"):
                    # v is a unicode instance
                    notes.append(Note("-".join(map(str, [v, self.OCTAVE]))))
                    if t:  # t 不为 0, 表明已经键入了音符, 计算时值
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
            elif key == "\r":  # 回车键表示演奏完毕, 将进行遗传进化
                durations.append(  # 计算最后一个音符的时值
                    time2duration(time.time() - t, self.STANDARD_DURATION)
                )
                # 同 abc
                prepared = [(
                    note.octave * 12 + name2int[note.name] + round(
                        duration) / 100.0, 1.0 / duration) for note, duration in
                    zip(notes, durations)]
                improvisation = gen.init_pop_from_seq(prepared)

                try:
                    pop, log = evolver.evolve_bar_nc(
                        improvisation, ngen=ngen, mu=len(improvisation),
                        cxpb=cxpb
                    )
                    print(len(set([i.tostring() for i in pop])) / len(pop))
                    pop.append(improvisation[-1])
                    # 输入交互式的尾小节, 寻找最匹配的起始小节
                    pop = compose(pop, mu=len(pop), selected=improvisation[-1])

                    durations, pitchs = zip(*[
                        math.modf(note) for ind in improvisation + pop for note
                        in ind
                    ])
                    notes = [
                        None if pitch == 1000 else Note().from_int(int(pitch))
                        for pitch in pitchs
                    ]
                    durations = [
                        int(round(duration * 100)) for duration in durations
                    ]

                    track = Track()
                    for note, duration in zip(notes, durations):
                        track.add_notes(note, duration)

                    after_composing(track, fn="interact")

                    visualize_log(log, fn="interact")

                    fluidsynth.play_Track(track[len(improvisation):])

                except KeyboardInterrupt:
                    pass

                finally:  # reset notes, durations and t
                    del notes[:]
                    del durations[:]
                    t = 0
            else:
                pass


if __name__ == '__main__':
    fire.Fire(Controller)
