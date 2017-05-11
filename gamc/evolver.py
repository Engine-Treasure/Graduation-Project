# -*- coding: utf-8 -*-

from __future__ import division

import random
import math
from copy import deepcopy

import array
import click
import numpy as np
from deap import base
from deap import creator
from deap import tools

import crossover
import evaluate
import fortin2013
import gen
import mutation
from txtimg import boom
from mingus.midi import fluidsynth
from mingus.containers.note import Note
from mingus.containers.bar import Bar

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
# creator.create("BarFitness", base.Fitness,
#                weights=(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0))
creator.create("BarFitness", base.Fitness,
               weights=(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0))
# pitch.duration
creator.create("Bar", array.array, typecode="d", fitness=creator.BarFitness,
               by_human=0)

toolbox = base.Toolbox()

DURATION_RANGE = [1, 2, 4, 8, 16, 32]


toolbox.register("ind_bar", gen.init_bar)
toolbox.register("pop_bar", tools.initRepeat, list, toolbox.ind_bar)

toolbox.register("evaluate_bar", evaluate.evaluate_bar)
toolbox.register("mate_bar", crossover.cx_one_point_bar)
toolbox.register("mutate_bar", mutation.mutate_bar)
toolbox.register("preselect_bar", fortin2013.selTournamentFitnessDCD)
toolbox.register("select_bar", fortin2013.selNSGA2)


def evolve_bar_nc(pop=None, ngen=100, mu=100, cxpb=0.9, seed=None):
    """
    :param pop: 初始化种群, 若未给定, 将自动生成初始化种群
    :param ngen: 进化的最大代数
    :param cxpb: 交叉概率
    :param seed: 随机种子
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
    logbook.header = "gen", "evals", "avg, ""std", "min", "max"

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


def evolve_bar_c(pop=None, ngen=100, mu=100, cxpb=0.9, seed=None):
    """
    :param pop: 初始化种群, 若未给定, 将自动生成初始化种群
    :param ngen: 进化的最大代数
    :param mu: 种群大小, 实际进化采用的种群大小将以此为依据, 进行倍增
    :param cxpb: 交叉概率
    :param seed: 随机种子
    :return:
    """
    random.seed(seed)

    CATASTROPHE = 5     # 灾变倒数计时
    CUR_G = 0             # 连续满足条件, 灾变倒计时才倒数. 该变量用于记录当前进化时间

    # create and register statistics method
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)

    # create logbook for recording evolution info
    logbook = tools.Logbook()
    # evals 不知为何物
    logbook.header = "gen", "evals", "avg, ""std", "min", "max"

    # not None means the pop is produced from abc file or keyboard
    if not pop:
        if mu >= 1000:
            N = mu
        elif mu >= 100:
            N = mu * 5
        elif mu > 0:
            N = mu * 50
        else:
            raise ValueError

        pop = toolbox.pop_bar(n=N)  # get initial populiation

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate_bar, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select_bar(pop, len(pop))

    # 记录日志
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

        for b in tools.selRandom(pop, 10):
            durations, pitchs = zip(*[math.modf(note) for note in b])
            notes = [
                None if pitch == 1000 else Note().from_int(int(pitch))
                for pitch in pitchs
            ]
            durations = [
                int(round(duration * 100)) for duration in durations
            ]
            bar = Bar()
            for note, duration in zip(notes, durations):
                bar.place_notes(note, duration)
            while 1:
                fluidsynth.play_Bar(bar)
                key = click.getchar()
                if key == u"g":
                    b.by_human = 1
                    break
                elif key == u"b":
                    break

        record = stats.compile(pop)
        logbook.record(gen=gen, evals=len(invalid_ind), **record)
        print(logbook.stream)

        # 以多样性为依据进行灾变
        if len(set([i.tostring() for i in pop])) <= mu:
            if gen - CUR_G == 1:
                CUR_G = gen
                CATASTROPHE -= 1
            else:  # 说明多样性得到恢复, 重置灾变倒计时
                CUR_G = gen
                CATASTROPHE = 5

                # top_inds = tools.selBest(pop, SURVIVAL_SIZE)  # 更新 top

        if CATASTROPHE == 0:
            print(boom)  # 灾变发生的信号
            SURVIVAL_SIZE = int(mu * gen / ngen)  # 环境容纳量, 即灾变发生后幸存者数
            top_inds = sorted(pop, key=lambda ind: ind.fitness, reverse=True)[1:SURVIVAL_SIZE + 1]  # 近似最优解集合, 不包括最优解

            pop = toolbox.pop_bar(n=N - SURVIVAL_SIZE)  # 灾变的新生个体
            pop.extend(deepcopy(top_inds))

            invalid_ind = [ind for ind in pop if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate_bar, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            pop = toolbox.select_bar(pop, len(pop))
            CATASTROPHE = 5  # 重置灾变倒计时

            # if SURVIVAL_SIZE >= mu * 0.8:
            #     break

    # before return, shrink
    offspring = toolbox.preselect_bar(pop, len(pop))
    offspring = [toolbox.clone(ind) for ind in offspring]
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate_bar, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    pop = toolbox.select_bar(pop + offspring, mu)

    return pop, logbook
