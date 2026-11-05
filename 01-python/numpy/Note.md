# NumPy：数组计算入门

安装：`python -m pip install numpy`。以下代码按顺序执行。路线：形状 → 索引 → 广播 → 矩阵运算 → 数据预处理。

[TOC]

## 数组、形状与类型

```python
import numpy as np
x = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
assert x.shape == (2, 3)
assert x.ndim == 2
print(x.dtype, np.zeros((2, 3)), np.arange(6).reshape(2, 3))
print(np.linspace(0, 1, 5))
```

shape 记录各轴长度，ndim 是轴数，dtype 是元素类型。二维机器学习数据常按 `(样本数, 特征数)` 排列。reshape 保持元素总数不变，可用一个 -1 自动推导长度。

## 索引、视图与副本

```python
assert x[1, 2] == 6
assert x[:, 1].shape == (2,)
assert x[:, 1:2].shape == (2, 1)
assert np.array_equal(x[x > 3], [4, 5, 6])
view = x[:, :2]
assert np.shares_memory(x, view)
independent = view.copy()
independent[0, 0] = 99
assert x[0, 0] == 1
```

基本切片通常共享原数组内存；布尔索引与整数数组索引返回副本。注意 `(N,)` 与 `(N, 1)` 在广播中行为不同。

## 广播与聚合

```python
bias = np.array([10, 20, 30], dtype=np.float32)
assert (x + bias).shape == (2, 3)
centered = x - x.mean(axis=1, keepdims=True)
assert np.allclose(centered.mean(axis=1), 0)
```

广播从右向左比较维度，长度相同或其中一个为 1 才兼容。axis=0 消去行轴，得到每列统计；axis=1 消去列轴，得到每行统计。keepdims 保留长度为 1 的轴，方便广播。

## 元素乘法与矩阵乘法

```python
assert (x * x).shape == (2, 3)
assert np.array_equal(x @ np.ones((3, 1)), [[6], [15]])
a = np.array([[2., 0.], [0., 4.]])
b = np.array([6., 8.])
solution = np.linalg.solve(a, b)
assert np.allclose(a @ solution, b)
```

星号逐元素相乘，@ 执行矩阵乘法。求解非奇异方阵线性系统使用 solve；最小二乘问题可使用 lstsq。

## 实践：拆分数据并标准化

```python
rng = np.random.default_rng(42)
samples = rng.normal(size=(100, 3))
order = rng.permutation(len(samples))
train, test = samples[order[:80]], samples[order[80:]]
mean = train.mean(axis=0, keepdims=True)
std = train.std(axis=0, keepdims=True)
scale = np.where(std > 1e-8, std, 1.0)
train_scaled = (train - mean) / scale
test_scaled = (test - mean) / scale
assert np.allclose(train_scaled.mean(axis=0), 0, atol=1e-7)
assert np.isfinite(test_scaled).all()
```

只用训练集计算均值和标准差，测试集复用这些参数，避免信息泄漏。常数列需要防止除零；真实数据还应处理缺失值。固定种子帮助复现，同时应记录 NumPy 版本。

## 保存与读取

```python
from tempfile import TemporaryDirectory
from pathlib import Path
with TemporaryDirectory() as directory:
    path = Path(directory) / "features.npy"
    np.save(path, train_scaled)
    assert np.allclose(np.load(path, allow_pickle=False), train_scaled)
```

## 排错与练习

|现象|检查点|
|---|---|
|广播错误|打印双方 shape，从右向左比较|
|修改切片影响原数组|是否需要 copy|
|原地运算类型错误|整数数组是否接收浮点结果|
|内存过大|广播是否创建巨大中间数组|

练习：筛选第一列为正的行；计算每列最大值；为标准化增加常数列测试。

参考：[NumPy 快速入门](https://numpy.org/doc/stable/user/quickstart.html)、[广播](https://numpy.org/doc/stable/user/basics.broadcasting.html)。下一步：[PyTorch](../../03-machinelearning/pytorch/Note.md)。
