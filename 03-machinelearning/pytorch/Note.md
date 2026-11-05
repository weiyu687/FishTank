# PyTorch：从张量到完整训练流程

前置知识：Python 函数与类、[NumPy](../../01-python/numpy/Note.md)、导数与矩阵乘法。路线：Tensor → 自动求导 → 数据加载 → 网络 → 训练与验证 → 保存恢复。

[TOC]

## 安装与环境

根据系统和 GPU 在 [官方安装页](https://pytorch.org/get-started/locally/)选择安装命令。本教程使用 CPU，无需下载数据集。建议使用独立虚拟环境，并核对官方支持的 Python 版本。

```python
import torch
print(torch.__version__)
print(torch.cuda.is_available())
```

## 张量与自动求导

```python
import torch
x = torch.tensor([[1., 2.], [3., 4.]])
assert x.shape == (2, 2)
assert x.unsqueeze(0).shape == (1, 2, 2)
weight = torch.tensor(3., requires_grad=True)
loss = (2 * weight - 4) ** 2
loss.backward()
assert weight.grad.item() == 8.0
```

导数为 `2 * (2 * weight - 4) * 2`，代入 3 得 8。梯度累积在 grad 中，每批训练前要清零。浮点特征通常为 float32，类别标签为 long；模型与输入必须处于兼容设备。

`tensor.detach().cpu().numpy()` 可转换为 NumPy；detach 切断梯度追踪但不复制内存。不要用 item 构造后续损失，它会将数值移出计算图。

## 完整实验：二维点二分类

将下面代码保存为 Python 文件即可运行。目标是判断两个特征的和是否大于零，前 400 条训练，其余验证。

```python
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader

torch.manual_seed(42)
features = torch.randn(512, 2)
labels = (features[:, 0] + features[:, 1] > 0).long()
train_data = TensorDataset(features[:400], labels[:400])
valid_data = TensorDataset(features[400:], labels[400:])
train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
valid_loader = DataLoader(valid_data, batch_size=64)

class Classifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(2, 16), nn.ReLU(), nn.Linear(16, 2))

    def forward(self, inputs):
        return self.layers(inputs)

model = Classifier()
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.02)

for epoch in range(20):
    model.train()
    total_loss = 0.0
    for inputs, targets in train_loader:
        optimizer.zero_grad(set_to_none=True)
        loss = loss_fn(model(inputs), targets)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(inputs)
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for inputs, targets in valid_loader:
            predictions = model(inputs).argmax(dim=1)
            correct += (predictions == targets).sum().item()
            total += len(targets)
    if epoch == 0 or (epoch + 1) % 5 == 0:
        print(f"epoch={epoch + 1:02d} loss={total_loss / len(train_data):.4f} accuracy={correct / total:.3f}")

assert correct / total > 0.9
```

输入与输出形状分别为 `(batch, 2)` 和 `(batch, 2)`，标签为 `(batch,)`。CrossEntropyLoss 接收原始 logits，前面不要添加 softmax。清梯度 → 前向 → 反向 → 更新构成训练循环。平均 loss 按样本数加权。

eval 调整 Dropout、BatchNorm 等层的行为；no_grad 关闭梯度记录，两者职责不同。验证数据不参与参数更新。固定种子帮助复现，不保证不同设备和版本结果完全一致。

## 保存与推理

接在完整实验后执行。临时目录用于演示，正式项目改用持久目录。

```python
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as directory:
    checkpoint = Path(directory) / "classifier.pt"
    torch.save(model.state_dict(), checkpoint)
    restored = Classifier()
    restored.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
    restored.eval()
    with torch.no_grad():
        point = torch.tensor([[2., 1.]])
        print(restored(point).softmax(dim=1))
        assert torch.allclose(model(point), restored(point))
```

恢复参数需要相同模型结构。断点续训还应保存优化器状态、epoch 和配置。仅加载可信来源文件。

## 排错与练习

|问题|检查点|
|---|---|
|设备不一致|模型、输入和标签是否都移动到目标 device|
|loss 不下降|标签、学习率、zero_grad 与 step|
|矩阵尺寸错误|打印每层 shape，核对 Linear 输入宽度|
|标签类型错误|分类索引应为 long|
|验证占用内存增加|关闭梯度，避免保留带计算图的张量|

1. 将标签改为 `features.square().sum(dim=1) < 1`，观察非线性网络如何学习圆形边界。
2. 比较不同隐藏层宽度和学习率，记录训练损失与验证准确率。
3. 改成预测特征之和：输出一个值，使用 MSELoss，并对齐预测与标签形状。
4. 继续学习自定义 Dataset、CNN、学习率调度和 GPU 训练。

参考：[官方基础教程](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)、[优化训练循环](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html)。
