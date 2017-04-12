# -*- coding: utf-8 -*-

from __future__ import division

import random

import mingus.extra.lilypond as lp
import numpy as np
from deap import base
from deap import creator
from deap import tools
from mingus.containers import Bar, Track
from mingus.midi import midi_file_out, fluidsynth

import evaluate
import fortin2013
from abcparse import parse_abc
from common import construct_bars, count
from gen import init_bar, init_sentence
from goperator import crossover, mutation

__author__ = "kissg"
__date__ = "2017-03-10"


creator.create("BarFitness", base.Fitness, weights=(1.0, 1.0, 1.0, 1.0, 1.0,
                                                    1.0, 1.0))
creator.create("Bar", Bar, fitness=creator.BarFitness)

toolbox = base.Toolbox()
# creator.Bar inherits from mingus.containers.Bar, and has attribute `fitness`
toolbox.register("bar", init_bar, creator.Bar, key="C", meter=(4, 4))
toolbox.register("pop_bar", tools.initRepeat, list, toolbox.bar)

toolbox.register("evaluate_bar", evaluate.evaluate_bar)
toolbox.register("mate_bar", crossover.cross_bar, ppb=None, dpb=None)
toolbox.register("mutate_bar", mutation.mutate_bar, indpb=0.10, ppb=None,
                 dpb=None)
toolbox.register("preselect_bar", fortin2013.selTournamentFitnessDCD)
toolbox.register("select_bar", fortin2013.selNSGA2)


def evolve_bar(pop=None, ngen=100, mu=100, cxpb=0.9, seed=None):
    random.seed(seed)

    CATASTROPHE = 10    # catastrophe countdown
    SURVIVAL_SIZE = 10  # initial survival size

    # create and register statistics method
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("max", np.max)
    stats.register("min", np.min)

    # create logbook for recording evolution info
    logbook = tools.Logbook()
    # evals in Chinese is 评价?
    logbook.header = "gen", "evals", "std", "min", "avg", "max"

    # not None means the pop is produced from abc file or keyboard
    if not pop:
        pop = toolbox.pop_bar(n=mu)

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate_bar, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select_bar(pop, len(pop))

    top_inds = tools.selBest(pop, SURVIVAL_SIZE)  #

    record = stats.compile(pop)
    logbook.record(gen=0, evals=len(invalid_ind), **record)
    print(logbook.stream)

    # Begin the generational process
    for gen in range(1, ngen):
        # Vary the population
        offspring = toolbox.preselect_bar(pop, len(pop))
        offspring = [toolbox.clone(ind) for ind in offspring]

        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
            if random.random() <= cxpb:
                toolbox.mate_bar(ind1, ind2)

            toolbox.mutate_bar(ind1)
            toolbox.mutate_bar(ind2)
            del ind1.fitness.values, ind2.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate_bar, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Select the next generation population
        pop = toolbox.select_bar(pop + offspring, mu)
        record = stats.compile(pop)
        logbook.record(gen=gen, evals=len(invalid_ind), **record)
        print(logbook.stream)

        print(len(set(top_inds) - set(tools.selBest(pop, SURVIVAL_SIZE))))
        if len(set(top_inds) - set(
                tools.selBest(pop, SURVIVAL_SIZE))) / SURVIVAL_SIZE <= 0.2:
            CATASTROPHE -= 1
            print(CATASTROPHE)
            # top_inds = tools.selBest(pop, SURVIVAL_SIZE)  # 更新 top

        if CATASTROPHE == 0:
            print("BOOM")
            new_pop = toolbox.pop_bar(n=(mu - SURVIVAL_SIZE))  # 灾变的新生个体
            pop = top_inds.extend(new_pop)
            SURVIVAL_SIZE += 10  # 环境容纳量
            top_inds = tools.selBest(pop, SURVIVAL_SIZE)  # 更新 top
            CATASTROPHE = 10  # 重置灾变倒计时

    return pop, logbook


def evolve_sentence(seed=None):
    random.seed(seed)

    NGEN = 10
    MU = 100
    CXPB = 0.9

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("max", np.max)
    stats.register("min", np.min)

    logbook = tools.Logbook()
    logbook.header = "gen", "evals", "std", "min", "avg", "max"

    pop = toolbox.pop_sentence(n=MU)

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]

    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select(pop, len(pop))

    record = stats.compile(pop)
    logbook.record(gen=0, evals=len(invalid_ind), **record)
    print(logbook.stream)

    # Begin the generational process
    for gen in range(1, NGEN):
        # Vary the population
        offspring = toolbox.preselect(pop, len(pop))
        # offspring = [toolbox.clone(ind) for ind in offspring]
        for ind in offspring:
            toolbox.clone(ind)

        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
            if random.random() <= CXPB:
                toolbox.mate(ind1, ind2)

            toolbox.mutate(ind1)
            toolbox.mutate(ind2)
            del ind1.fitness.values, ind2.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Select the next generation population
        pop = toolbox.select(pop + offspring, MU)
        record = stats.compile(pop)
        logbook.record(gen=gen, evals=len(invalid_ind), **record)
        print(logbook.stream)

    return pop, logbook


if __name__ == '__main__':
    fluidsynth.init(
        sf2="/home/kissg/Developing/Graduation-Project/src/statics/soundfonts/JR_elepiano.sf2",
        driver="alsa")
    key, meter, notes = parse_abc(
        "/home/kissg/Developing/Graduation-Project/data/ABCs/999.abc")
    notes, durations = zip(*[(note[0].rstrip("*"), note[1]) for note in notes])
    notes = [note[:-1].upper() + "-" + note[-1] for note in notes]

    print(key, meter, notes, durations)

    pop = construct_bars(notes, durations, container=creator.Bar)
    track3 = Track()
    for i, bar in enumerate(pop, 16):
        track3.add_bar(bar)
    lp.to_pdf(lp.from_Track(track3), "origin.pdf")

    midi_file_out.write_Track("origin.mid", track3)
    # for p in pop:
    #     print(p)
    #     fluidsynth.play_Bar(p)

    toolbox.unregister("mate_bar")
    toolbox.unregister("mutate_bar")
    ppb, dpb = count(notes, durations)
    print(ppb)
    toolbox.register("mate_bar", crossover.cross_bar, ppb=ppb, dpb=dpb)
    toolbox.register("mutate_bar", mutation.mutate_bar, indpb=0.10, ppb=ppb,
                     dpb=dpb)

    bars_pool, log_bar = evolve_bar(pop=pop)
    # print(
    #     "Best individual is: {}\n with fitness: {}".format(hof[0],
    #                                                        hof[0].fitness))
    print(len(set(bars_pool)))
    track2 = Track()
    for i, bar in enumerate(tools.selTournament(bars_pool, 16, 4)):
        track2.add_bar(bar)

    lp.to_pdf(lp.from_Track(track2), "top_bar.pdf")

    midi_file_out.write_Track("top_bar.mid", track2)

    creator.create("SentenceFitness", base.Fitness,
                   weights=(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0))
    creator.create("Sentence", list, fitness=creator.SentenceFitness,
                   bars_pool=[])

    toolbox.register("sentence", init_sentence, creator.Sentence,
                     bars_pool=bars_pool)
    toolbox.register("pop_sentence", tools.initRepeat, list, toolbox.sentence)

    toolbox.register("evaluate", evaluate.evaluate_sentence)
    toolbox.register("mate", crossover.cross_sentence)
    toolbox.register("mutate", mutation.mutate_sentence)
    toolbox.register("preselect", fortin2013.selTournamentFitnessDCD)
    toolbox.register("select", fortin2013.selNSGA2)
    # toolbox.register("select", tools.selTournament, tournsize=3)

    pop_sentence, log_sentence = evolve_sentence()

    track = Track()
    for i, sentence in enumerate(tools.selRoulette(pop_sentence, 4)):
        for bar in sentence:
            track.add_bar(bar)

    lp.to_pdf(lp.from_Track(track), "top_sentence.pdf")

    midi_file_out.write_Track("top_sentence.mid", track)
    exit(0)
