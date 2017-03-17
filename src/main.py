# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-10"

import random

from deap import base
from deap import tools
from deap import creator
from pysynth_e import make_wav

NOTES = [1, 1.5, 2, 2.5, 3, 4, 4.5, 5, 5.5, 6, 6.5, 7]  # 音符编码
OCTAVE = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # 八度编码
DURATION = [1, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625]  # 时值编码, 最小 1/6

# 适应度函数, `weights` weights 的每一项表示一个观测值
# 暂定为 (1.0,), 表示最大化协和度
creator.create("Fitness", base.Fitness, weights=(1.0,))

# 以小节为个体, list 形式表示
# meter: (4, 4), 四四拍, 前一个 4 表示以 4 分音符为一拍, 后一个 4 表示 4 拍为一个小节
# [((1, 5, 4), (1.5, 5, 4), (3, 5, 4), (5, 5, 4))]
creator.create("Individual", list, fitness=creator.Fitness, meter=tuple)


def initial_individual():
    pass


toolbox = base.Toolbox()
# 此处随机生成种群的个体
# 注: toolbox.register(alias, func, args_for_func)
# 注: tools.initRepeat(container, generator_func, repeat_times)

ind1 = toolbox.gen_individual()
a = len(ind1) - 1
song = [("".join(ind1[0:a]), ind1[a])] * 10
print(song)
make_wav(song, fn="a.wav")
