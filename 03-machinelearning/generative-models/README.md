# 生成模型数学基础

从第一性原理建立生成模型所需的数学知识链。目标不是记忆公式，而是理解每一个公式从哪里来、为什么成立，以及它在模型中解决什么问题。

## 路线与进度

- ✅ Part I 数学语言：函数、概率、条件概率、随机变量、概率密度、期望与方差
- ✅ Part II 概率模型：高斯分布、多维高斯、log、似然、最大似然估计
- ✅ Part III 信息与推断：信息量、熵、交叉熵、KL、贝叶斯、潜变量模型
- ✅ Part IV 变分推断：难解后验、近似后验、Jensen、ELBO
- ✅ Part V VAE：从 AE 到 VAE、重参数化、KL 与重建项
- ✅ Part VI Diffusion：前向扩散、反向过程、DDPM、Score
- ✅ Part VII Flow Matching：ODE、向量场、概率路径、连续性方程、CFM
- ✅ Part VIII 统一视角：VAE / Diffusion / Score / Flow Matching

网页版本现作为 FishTank 知识树中的独立知识体系，位于 `docs/generative-models/`，由同一个 GitHub Pages 站点托管。

## 内容原则

1. 新概念必须能追溯到已介绍的概念。
2. 关键公式不跳步；每个重要等号或不等号说明依据。
3. 同时给出直觉解释、数学定义、生成模型中的作用。
4. 若某个数学工具暂不展开证明，会明确标记为可选深入或后续章节内容。


## 第一阶段课程状态

✅ 核心八个 Part 已全部完成：从零基础概率论一路建立到 VAE、Diffusion、Score 与 Flow Matching 的统一视角。

后续可作为第二阶段继续扩展专题附录：线性代数、多元微积分、SDE、DDIM、Classifier-Free Guidance、Latent Diffusion、Rectified Flow、OT-CFM、Schrödinger Bridge 等。


## Pages 信息架构

- `docs/index.html`：FishTank 总知识树主页
- `docs/generative-models/index.html`：生成模型数学基础课程首页
- `docs/generative-models/part1.html` ～ `part8.html`：八个完整 Part
- `docs/part1.html` ～ `part8.html`：兼容旧链接的重定向页

后续新增知识体系时，在 `docs/<knowledge-system>/` 下建立独立子站，并从 FishTank 总知识树主页添加入口即可，无需新增 GitHub Pages 项目。
