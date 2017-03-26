from __future__ import division

import os
import glob
from fractions import Fraction
from collections import Counter, OrderedDict

import numpy as np
import joblib

import my_read_abc


if not os.path.exists("ABCs"):
    os.makedirs("ABCs")


with open("session_data_clean.txt") as f:
    abcs = f.read().split("\n\n")


for i, abc in enumerate(abcs):
    with open(os.path.join("ABCs", str(i) + ".abc"), "w") as f:
        f.write(abc + "\n\n")






