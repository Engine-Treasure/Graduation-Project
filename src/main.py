# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-10"

import random

from deap import base
from deap import creator
from pysynth_e import make_wav

IND_SIZE = 1

# 适应度函数, `weights` 的每一维表示某项适应度的权值
creator.create("Fitness", base.Fitness, weights=(1.0,))
# 个体, 以 list 形式表示
creator.create("Individual", tuple, fitness=creator.Fitness)


def initial_individual():

    def get_degree():
        # 在不了解作曲家谱曲, 各音名使用频率, 采用完全随机的方式
        return random.SystemRandom().choice("cdefgabr")

    def get_accidental():
        # `c#` 和 `db` 是同一个音
        return random.SystemRandom().choice(["#", ""])

    def get_octave():
        # 八度, 不知道是什么
        return random.SystemRandom().choice("012345678")

    def get_louder():
        # 响亮一点?
        return random.SystemRandom().choice(["*", ""])

    def get_duration():
        return random.SystemRandom().choice([1, 2, -2, 4, -4, 8, -8,
                                             16, -16, 32, -32])
    return (get_degree(), get_accidental(), get_octave(), get_louder(),
            get_duration())


toolbox = base.Toolbox()
# 此处随机生成种群的个体
# 注: toolbox.register(alias, func, args_for_func)
# 注: tools.initRepeat(container, generator_func, repeat_times)
toolbox.register("gen_individual", initial_individual)

ind1 = toolbox.gen_individual()
a = len(ind1) - 1
song = [("".join(ind1[0:a]), ind1[a])] * 10
print(song)
make_wav(song, fn="a.wav")

