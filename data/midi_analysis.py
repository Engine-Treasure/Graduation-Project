# -*- coding: utf-8 -*-
from __future__ import division

import os
import json
import glob
import copy
from collections import Counter

import midi
import numpy as np
# import joblib

import send_email

__author__ = "kissg"
__date__ = "2017-03-28"

NAME = {0: "C", 1: "C#", 2: "D", 3: "D#", 4: "E", 5: "F", 6: "F#", 7: "G",
        8: "G#", 9: "A", 10: "A#", 11: "B"}


def get_N_grams(_input, n):
    output = dict()  # store n-tuple
    # str or float
    # if isinstance(_input[0], float):
    #     _input = [
    #         str(Fraction(1 / ele).limit_denominator(32)) for ele in _input
    #         ]
    for i in range(len(_input) - n + 1):
        n_gram = ' '.join(_input[i: i + n])  # 相邻的单词构成一个n元组
        if n_gram in output:  # 统计n元组的词频
            output[n_gram] += 1
        else:
            output[n_gram] = 1
    return output


def pitch2name(pitch):
    a, b = divmod(pitch, 12)
    name = NAME[b]
    octave = str(a - 1)
    return name + octave


def compute_pitch_statistics(midi_file):
    """
    :param midi_file: str - path to a MIDI file
    :return:
    """
    try:
        pattern = midi.read_midifile(midi_file)

        pitchs = [
            event.get_pitch()
            for track in pattern
            for event in track if isinstance(event, midi.NoteEvent)
            ]
        pitchs = map(pitch2name, pitchs)

        pitch_2 = get_N_grams(pitchs, 2)
        pitch_3 = get_N_grams(pitchs, 3)
        pitch_4 = get_N_grams(pitchs, 4)
        pitch_5 = get_N_grams(pitchs, 5)
        pitch_6 = get_N_grams(pitchs, 6)

        return {"pitch": Counter(pitchs),
                "pitch_2": Counter(pitch_2),
                "pitch_3": Counter(pitch_3),
                "pitch_4": Counter(pitch_4),
                "pitch_5": Counter(pitch_5),
                "pitch_6": Counter(pitch_6)}
    except Exception as e:
        pass


def concat_pitch_statistics(a, b):
    for k, v in b.iteritems():
        if k in a.keys():
            a[k].update(v)  # update Counter
        else:
            a[k] = copy.deepcopy(v)
    return a


# pitch_statistics = joblib.Parallel(n_jobs=10, verbose=0)(
#     joblib.delayed(compute_pitch_statistics)(midi_file)
#     for midi_file in glob.glob(
#         os.path.join("MIDIs", "*.[mM][iI][dD]"))
# )

subdirs = os.listdir("lmd_full")
for subdir in subdirs:
    pitch_statistics = (compute_pitch_statistics(midi_file)
                        for midi_file in
                        glob.iglob(os.path.join("lmd_full", subdir, "*.[mM][iI][dD]")))

    pitch_statistics = (s for s in pitch_statistics if s is not None)

    pitch_statistics = reduce(concat_pitch_statistics, pitch_statistics)

    with open("midi_result" + subdir, "w") as f:
        f.write(json.dumps(pitch_statistics))

#
# with open("midi_result", "w") as f:
#     f.write(json.dumps(pitch_statistics))

send_email.send_email()
