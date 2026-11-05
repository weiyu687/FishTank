# FishTank · 个人知识库

从基础编程到智能体与机器学习，记录概念、推导与可复用实验。

[在线阅读](https://weiyu687.github.io/FishTank/)

## 目录

- [Python](01-python/)：版本管理、os 与 pathlib。
- [LangChain](02-langchain/)：Agent 实验与示例。
- [机器学习](03-machinelearning/)：强化学习六阶段笔记与实验。
  - [生成模型数学基础](03-machinelearning/generative-models/)：八章课程，保留原内容。

## 更新与发布

以各章节中的 Markdown 和 Jupyter Notebook 为内容源。新增笔记、图片或实验后，运行：

```sh
pip install -r requirements-site.txt
python scripts/build_site.py
```

生成结果位于 `docs/`。Notebook 仅渲染已有代码和输出，不执行代码。生成模型网页保持在 `docs/generative-models/`，原链接继续有效。

推送至 main 后，GitHub Actions 自动构建并部署 Pages。仓库 Settings → Pages 的 Source 应设置为 GitHub Actions。也可使用 main 分支的 docs 目录发布已提交的生成结果。
