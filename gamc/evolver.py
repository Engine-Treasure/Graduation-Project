# -*- coding: utf-8 -*-

from __future__ import division

import random
from copy import deepcopy

import array
import math
import numpy as np
from deap import base
from deap import creator
from deap import tools

import abcparse
import common
import crossover
# import fortin2013
import engine2017 as fortin2013
import evaluate
import gen
import mutation
import util
from statistics import duration_frequencies as duration_probability

__author__ = "kissg"
__date__ = "2017-03-10"

# 多目标, 依次为
#   相邻音符的协和度
#   相邻音符的音程
#   相邻音符的时值差
#   马尔可夫经验
#   音符所在区间
#   小节长度
#   音高变化
#   时值变化
#   音高多样性
#   时值多样性
creator.create("BarFitness", base.Fitness, weights=(1.0, 0.7, 1.0, 1.0, 0.4, 0.4, 0.4, 0.7, 0.4, 0.7))
# pitch.duration
creator.create("Bar", array.array, typecode="d", fitness=creator.BarFitness)

toolbox = base.Toolbox()

PITCH_LOW, PITCH_UP = 0, 96
DURATION_RANGE = [1, 2, 4, 8, 16, 32]


def get_pitch():
    # return random.randint(low, up)
    # pitch = np.random.choice(range(0, 88), p=pitch_probability)
    # return pitch if 36 <= pitch <= 83 else get_pitch()
    # pitch = np.random.choice([
    #     45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67
    # ])
    pitch = np.random.choice([
        36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69
    ])
    return pitch


def get_duration(_range):
    available_probability = duration_probability[-len(_range):]
    new_total = sum(available_probability)
    probality = [_ / new_total for _ in available_probability]  # 重新计算比例
    duration = np.random.choice(_range, p=probality)
    return duration


def init_bar():
    rest = 1
    ind_bar = creator.Bar()
    while rest:
        pitch = get_pitch()
        duration = get_duration(
            [dt for dt in range(int(math.ceil(1 / rest)), 65, 1) if
             dt in DURATION_RANGE])
        ind_bar.append(pitch + duration / 100)
        rest -= 1 / duration
    return ind_bar


toolbox.register("ind_bar", init_bar)
toolbox.register("pop_bar", tools.initRepeat, list, toolbox.ind_bar)

toolbox.register("evaluate_bar", evaluate.evaluate_bar)
toolbox.register("mate_bar", crossover.cx_one_point_bar)
toolbox.register("mutate_bar", mutation.mutate_bar)
toolbox.register("preselect_bar", fortin2013.selTournamentFitnessDCD)
toolbox.register("select_bar", fortin2013.selNSGA2)


def evolve_bar_nc(pop=None, ngen=100, mu=100, cxpb=0.9, mutpb=0.1, seed=None):
    """
    :param pop: population, if None, pop_bar will be called for producing bars
    :param ngen: evolution times
    :param mu:
    :param cxpb: crossover probability
    :param seed:
    :return:
    """
    random.seed(seed)

    # create and register statistics method
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("max", np.max, axis=0)
    stats.register("min", np.min, axis=0)

    # create logbook for recording evolution info
    logbook = tools.Logbook()
    # evals in Chinese is 评价?
    logbook.header = "gen", "evals", "std", "min", "avg", "max"

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate_bar, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select_bar(pop, len(pop))

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
                a = deepcopy(ind1)
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

    return pop, logbook


def evolve_bar_c(pop=None, ngen=100, mu=100, cxpb=0.9, mutpb=0.1, seed=None):
    """
    带灾变的小节进化
    :param pop: population, if None, pop_bar will be called for producing bars
    :param ngen: evolution times
    :param mu:
    :param cxpb: crossover probability
    :param seed:
    :return:
    """
    random.seed(seed)

    CATASTROPHE = 5  # catastrophe countdown
    SURVIVAL_SIZE = 10  # initial survival size
    CUR = 0

    # create and register statistics method
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("max", np.max, axis=0)
    stats.register("min", np.min, axis=0)

    # create logbook for recording evolution info
    logbook = tools.Logbook()
    # evals in Chinese is 评价?
    logbook.header = "gen", "evals", "std", "min", "avg", "max"

    # not None means the pop is produced from abc file or keyboard
    if not pop:

        if mu >= 1000:
            N = mu
        elif mu >= 100:
            N = mu * 2
        elif mu > 0:
            N = mu * 20
        else:
            raise ValueError

        pop = toolbox.pop_bar(n=N)

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate_bar, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select_bar(pop, len(pop))

    # todo: for catastrophe
    top_inds = tools.selBest(pop, SURVIVAL_SIZE)  # top  individuals to survive

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
        # pop = toolbox.select_bar(pop + offspring, mu)
        pop = toolbox.select_bar(pop + offspring, len(pop))

        record = stats.compile(pop)
        logbook.record(gen=gen, evals=len(invalid_ind), **record)
        print(logbook.stream)

        # todo: for catastrophe
        # 以适应度函数平均值和标准差为依据进行灾变
        if util.cal_variance(logbook.select("avg")[-2].tolist(),
                             logbook.select("avg")[-1].tolist()) < 0.001 and \
                        util.cal_variance(logbook.select("std")[-2].tolist(),
                                          logbook.select("std")[
                                              -1].tolist()) < 0.001:
        # 以多样性为依据进行灾变
        # if len(set([i.tostring() for i in pop])) <= mu:
            print("B", CUR, gen)
            print(CATASTROPHE)
            if gen - CUR == 1:
                CUR = gen
                CATASTROPHE -= 1
            else:
                print("Ck")
                CUR = gen
                CATASTROPHE = 5

            # top_inds = tools.selBest(pop, SURVIVAL_SIZE)  # 更新 top

        if CATASTROPHE == 0:
            print(("BOOM " * 10 + "\n") * 10)
            pop = toolbox.pop_bar(n=(N - SURVIVAL_SIZE))
            pop.extend(deepcopy(top_inds))  # 灾变的新生个体

            invalid_ind = [ind for ind in pop if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate_bar, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            pop = toolbox.select_bar(pop, len(pop))
            print(int(mu * gen / ngen))
            SURVIVAL_SIZE = int(mu * gen / ngen)  # 环境容纳量增大
            if SURVIVAL_SIZE == mu:
                return pop, logbook
            top_inds = tools.selBest(pop, SURVIVAL_SIZE)  # 更新 top

            CATASTROPHE = 5  # 重置灾变倒计时

    # offspring = toolbox.preselect_bar(pop, len(pop))
    # offspring = [toolbox.clone(ind) for ind in offspring]
    # invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    # fitnesses = toolbox.map(toolbox.evaluate_bar, invalid_ind)
    # for ind, fit in zip(invalid_ind, fitnesses):
    #     ind.fitness.values = fit
    # pop = toolbox.select_bar(pop + offspring, mu)

    df = common.cal_bar_similarity(pop)
    a = random.choice(df.keys())
    ma = df[a].argmax()
    nearby = df[a].nlargest(5)

    composition = [random.choice(pop)]
    for i in range(mu):
        idx = pop.index(composition[-1])
        # 从相似度最高的 5 个小节中选择一个, 获取其索引
        nxtidx = df[idx].nlargest(7).sample(1).keys()[0]
        composition.append(pop[nxtidx])

    return composition, logbook


def evolve_from_abc(abc, ngen=100, mu=None, cxpb=0.9, mutpb=0.1):
    key, meter, notes = abcparse.parse_abc(abc)
    names, durations = zip(*
                           [(note[0].rstrip("*"), note[1]) for note in notes])
    names = [(name[:-1].upper(), int(name[-1])) for name in names]
    pitchs = [name[1] * 12 + gen.name2int[name[0]] for name in names]
    prepare_pop = [(p + d / 100.0, 1.0 / d) for p, d in zip(pitchs, durations)]
    pop = gen.init_pop_from_seq(prepare_pop)

    # ppb, dpb = count(names, durations)
    #
    # toolbox.unregister("mate_bar")
    # toolbox.unregister("mutate_bar")
    # toolbox.register("mate_bar", crossover.cross_bar, ppb=ppb, dpb=dpb)
    # toolbox.register("mutate_bar", mutation.mutate_bar, ppb=ppb, dpb=dpb)
    mu = mu if mu else len(pop)

    evolved_pop, log = evolve_bar_nc(pop=pop, ngen=ngen, mu=mu, cxpb=cxpb,
                                     mutpb=mutpb)
    return evolved_pop, log
