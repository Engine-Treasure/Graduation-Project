# -*- coding: utf-8 -*-

from __future__ import division

from collections import OrderedDict
from itertools import islice
from math import ceil

import mingus.core.intervals as intervals
import mingus.extra.lilypond as lp
import numpy as np
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from mingus.containers import Bar, Note, Track
from mingus.midi import midi_file_out

import util
import gen
import evaluate
from goperator import crossover, mutation, selection
from config import pitch_frequencies, duration_frequencies

__author__ = "kissg"
__date__ = "2017-03-10"

creator.create("BarFitness", base.Fitness, weights=(1.0, 1.0, 1.0, 1.0, 1.0,))
# creator.create("TrackFitness", base.Fitness, weights=(1.0,))

creator.create("Bar", Bar, fitness=creator.BarFitness)
# creator.create("Track", Track, fitness=creator.TrackFitness)

toolbox = base.Toolbox()
# 此处随机生成种群的个体
# 注: toolbox.register(alias, func, args_for_func)
toolbox.register("bar", gen.init_bar, creator.Bar, key="C", meter=(4, 4))
toolbox.register("pop_bar", tools.initRepeat, list, toolbox.bar)
# toolbox.register("track", init.initTrack, creator.Track)

toolbox.register("mate", crossover.cxOnePoint)
toolbox.register("mutate", mutation.mutName, indpb=0.10)
toolbox.register("select", tools.selTournament, tournsize=4)
toolbox.register("evaluate", evaluate.evaluate_bar)


def main():
    pop = toolbox.pop_bar(n=100)
    for individual in pop:
        print(individual)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("max", np.max)
    stats.register("min", np.min)

    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2,
                                       ngen=5, stats=stats, halloffame=hof,
                                       verbose=True)
    return pop, logbook, hof


if __name__ == '__main__':
    pop, log, hof = main()
    print(
        "Best individual is: {}\n with fitness: {}".format(hof[0],
                                                           hof[0].fitness))

    print(pop)
    top16 = tools.selRandom(pop, 16)
    track = Track()
    for i, bar in enumerate(top16):
        print(bar)
        track.add_bar(bar)

    lp.to_pdf(lp.from_Track(track), "top.pdf")

    midi_file_out.write_Track("top.mid", track)



    # bars = [toolbox.bar() for i in range(100)]
    # [toolbox.evaluate(bar) for bar in bars]
    # results = (toolbox.evaluate(bar) for bar in bars)
    # for r in results:
    #     print(r)

    # bars = [toolbox.bar() for i in range(100)]
    #
    # bars_with_grade = {bar: evalute_bar(bar) for bar in bars}
    # bar_rank = OrderedDict(
    #     sorted(bars_with_grade.iteritems(), key=lambda t: t[1], reverse=True))
    # print(len(bar_rank))
    # print(bar_rank.values())
    #
    # top10_bars = islice(bar_rank.keys(), 10)
    # last10_bars = islice(bar_rank.keys(), 90, 100)
    #
    # for k, v in bar_rank.iteritems():
    #     print(v, k)
    #
    # track_top = toolbox.track(top10_bars)
    # track_last = toolbox.track(last10_bars)
    #
    # lp.to_pdf(lp.from_Track(track_top), "top.pdf")
    #
    # midi_file_out.write_Track("top.mid", track_top)
    #
    # lp.to_pdf(lp.from_Track(track_last), "last.pdf")
    #
    # midi_file_out.write_Track("last.mid", track_last)

    # track = toolbox.track(bars)
    # lp.to_pdf(lp.from_Track(track), "1.pdf")
    #
    # midi_file_out.write_Track("1.mid", track)
