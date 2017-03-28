# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-28"


from __future__ import division
import os
import glob
from collections import Counter

import midi
import numpy as np
import joblib


def compute_pitch_statistics(midi_file):
    """
    :param midi_file: str - path to a MIDI file
    :return:
    """
    try:
        pattern = midi.read_midifile(midi_file)
        return [
            event.get_pitch()
            for track in pattern
            for event in track if isinstance(event, midi.NoteEvent)
            ]
    except Exception as e:
        pass

pitch_statistics = joblib.Parallel(n_jobs=10, verbose=0)(
    joblib.delayed(compute_pitch_statistics)(midi_file)
    for midi_file in glob.glob(
        os.path.join(os.path.expanduser("~"), "Lab", "Data", "MIDIs", "*", "*.[mM][iI][dD]"))
)
