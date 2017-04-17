import os
import json
import glob
import copy
from collections import Counter


def combine_result(a, b):
    for k, v in b.iteritems():
        if k in a.keys():
            a[k].update(Counter(v))
        else:
            a[k] = Counter(copy.deepcopy(v))
    return a


def load_dict(fn):
    with open(fn) as f:
        return json.load(f)


midi_results = (load_dict(midi_result) for midi_result in glob.iglob(os.path.join("midi_result", "*.txt")))
combined_result = reduce(combine_result, midi_results, {})

with open("combined_result.txt", "w") as f:
    json.dump(combined_result, f)

