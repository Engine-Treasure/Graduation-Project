from cStringIO import StringIO
from collections import Counter

from src.read_abc import parse_abc


def get_abcs():
    with open(
            "/home/kissg/Developing/Graduation-Project/data/sessions_data_clean.txt") as f:
        abcs = (abc + "\n" for abc in f.read().split("\n\n"))
        return abcs


def clean(notes_list):
    return [note[0].rstrip("*") for note in notes_list]


counter = Counter()
failure = {}


def parse(abcs):
    global counter
    global failure

    for index, abc in enumerate(abcs):
        sio = StringIO(abc)
        try:
            notes_list = parse_abc(sio)
            pure_notes = clean(notes_list)
            counter.update(Counter(pure_notes))
            print("No.{index} abc, succeed.".format(index=index))
            print(abc)
        except Exception as e:
            failure.update({index: e.message + "\n" + abc})


# def parse(abcs):
#     counter = Counter()
#     global failure
#     for i, abc in enumerate(abcs):
#         sio = StringIO(abc)
#         try:
#             counter.update(Counter(clean(parse_abc(sio))))
#             print("No.{index} abc, succeed.".format(index=i))
#             print(abc)
#         except Exception as e:
#             failure.update({i: e.message + "\n" + abc})
#
#     return counter

if __name__ == '__main__':
    abcs = get_abcs()
    parse(abcs)
