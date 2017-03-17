# DEAP 笔记

1. 选择适合的类型 (`type`) with `creator`:

```python
creator.create(name, base_cls, kwargs)
```

2. 初始化种群 (`Toolbox` 遗传算法算子的容器类，包括初始化器)

```python
# alias - 算子别名
# args, kargs - 是传递给 function 的参数
toolbox.register(self, alias, function, *args, **kargs)
```

3. 算子. 有内建，也可以创建


```python
def evaluate(individual):
    return sum(individual),

toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)
```

4. 算法

> PS: 适应度值必须是可迭代的
