# Python 常用模块

标准库无需额外安装。建议按“文件与数据 → 容器与迭代 → 工程脚本”的顺序学习。已有专题：[pathlib](../pathlib/Note.md)、[os](../os/Note.md)。

[TOC]

## 文件与数据：pathlib、json、csv

Path 处理路径，JSON 保存嵌套配置，CSV 保存二维表格。示例使用临时目录，不覆盖已有文件。

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import csv

with TemporaryDirectory() as directory:
    folder = Path(directory)
    config = {"模型": "linear", "lr": 0.01}
    path = folder / "config.json"
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    assert json.loads(path.read_text(encoding="utf-8")) == config
    with (folder / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["epoch", "loss"])
        writer.writeheader()
        writer.writerow({"epoch": 1, "loss": 0.42})
```

JSON 不能直接保存任意 Python 对象；NumPy 数组需先转换。CSV 读取的数值通常是字符串，需要显式转换。读写文本应明确 encoding。

## 容器：collections

```python
from collections import Counter, defaultdict, deque
assert Counter(["cat", "dog", "cat"]).most_common(1) == [("cat", 2)]
groups = defaultdict(list)
for name, category in [("apple", "fruit"), ("pear", "fruit")]:
    groups[category].append(name)
queue = deque(["first", "second"])
queue.append("third")
assert queue.popleft() == "first"
```

Counter 用于计数，defaultdict 用于分组，deque 适合两端增删。访问 defaultdict 的缺失键会创建默认值，仅检查存在性时使用 `key in groups`。

## 迭代与缓存：itertools、functools

```python
from itertools import product, chain, islice
from functools import lru_cache
assert len(list(product([0.01, 0.1], [16, 32]))) == 4
assert list(chain([1, 2], [3])) == [1, 2, 3]
assert list(islice(iter(range(100)), 3)) == [0, 1, 2]

@lru_cache(maxsize=128)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

assert fib(10) == 55
```

迭代器通常只能消费一次。缓存参数需要可哈希；依赖外部可变状态的函数可能返回过期结果。

## 时间：datetime、time

```python
from datetime import datetime, timezone, timedelta
from time import perf_counter
now = datetime.now(timezone.utc)
assert now + timedelta(days=1) > now
start = perf_counter()
sum(range(10000))
print(now.isoformat(), perf_counter() - start)
```

datetime 表达时间点，perf_counter 测量耗时。不要混用带时区与无时区时间。

## 文本：re

```python
import re
match = re.search(r"loss=(\d+(?:\.\d+)?)", "epoch=3 loss=0.125")
assert match and float(match.group(1)) == 0.125
```

原始字符串减少反斜杠转义困扰。JSON、CSV 等结构化数据应优先使用专用解析器。

## 标量计算：math、statistics、random

```python
import math
import statistics
import random
assert math.isclose(0.1 + 0.2, 0.3)
assert statistics.mean([1, 2, 3]) == 2
print(random.Random(42).sample(range(10), 3))
```

math 适合标量，statistics 适合小型统计，大规模数组使用 NumPy。random 用于模拟；安全令牌使用 secrets。

## 工程脚本：argparse、logging、dataclasses

```python
import argparse
import logging
from dataclasses import dataclass

@dataclass
class Config:
    epochs: int = 10
    learning_rate: float = 0.01

parser = argparse.ArgumentParser(description="训练配置")
parser.add_argument("--epochs", type=int, default=10)
args = parser.parse_args(["--epochs", "5"])
if args.epochs <= 0:
    parser.error("epochs 必须大于零")
config = Config(epochs=args.epochs)
logging.basicConfig(level=logging.INFO)
logging.info("训练轮数：%s", config.epochs)
```

保存为脚本后，将 `parse_args([...])` 改为 `parse_args()`，即可从命令行传入 `--epochs 5`。

## 练习

读取 CSV 的 loss 列并计算平均值；用 Counter 统计日志事件；增加 `--learning-rate` 参数及正数校验。

参考：[Python 标准库](https://docs.python.org/zh-cn/3/library/index.html)。下一步：[NumPy](../numpy/Note.md)。
