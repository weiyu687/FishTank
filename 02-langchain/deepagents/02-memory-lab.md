# Deep Agents 记忆机制：原理、实验与排错

目标：能分别证明“数据被保存”“数据被重新读取”“数据影响回答”，并验证隔离、更新与遗忘。只问一句“你记住了吗”不足以验证记忆。

[TOC]

## 1. 四种容易混淆的状态

|对象|内容|生命周期|
|---|---|---|
|当前上下文|本次模型真正收到的消息和文件片段|一次模型调用|
|线程状态 / checkpoint|消息、工具调用和图状态|一个 thread 的连续执行|
|跨线程记忆|用户偏好、项目规则、稳定事实|由 store 或文件系统生命周期决定|
|模型参数|训练得到的统计规律|不会因普通对话写文件而更新|

Checkpointer 恢复一个线程；Store 保存应用定义的跨线程数据。InMemorySaver 和 InMemoryStore 都是进程内实现，重启会丢失。thread_id 是状态定位键，不能替代身份验证。[持久化文档](https://docs.langchain.com/oss/python/langgraph/persistence)

## 2. 记忆系统的完整链路

候选提取 → 判断是否值得记 → 校验来源和范围 → 去重与合并 → 写入 → 检索或加载 → 注入上下文 → 回答 → 验证效果。

例如“本项目使用 pytest”可以成为项目记忆；“今天先帮我写一句英文”通常只是当前任务。记忆条目宜包含 value、scope、source、updated_at、version、expires_at。过期事实不应因检索相似度高就继续被采用。

Deep Agents 的 memory 参数指定要加载的文件；AGENTS.md 可承载稳定说明。更新是否发生仍依赖写入路径、权限与 Agent 行为。Skills 更适合复用流程，启动时加载描述，任务匹配后再读全文。[记忆文档](https://docs.langchain.com/oss/python/deepagents/memory)、[Skills 文档](https://docs.langchain.com/oss/python/deepagents/skills)

## 3. 实验准备

实验脚本：[memory_probe.py](experiments/memory_probe.py)。仅使用专用实验目录、随机虚构偏好和可删除数据。不要用真实用户信息验证隔离。

安装 deepagents 与所选 provider 包，在终端设置 DEEPAGENT_MODEL 和对应 API 密钥。先运行 `python -m pip freeze` 记录环境。脚本会打印实际包版本；本仓库不声称某个未实测版本组合已经通过在线调用。

在仓库根目录执行：

```sh
python 02-langchain/deepagents/experiments/memory_probe.py --mode seed --user alice
python 02-langchain/deepagents/experiments/memory_probe.py --mode read --user alice
python 02-langchain/deepagents/experiments/memory_probe.py --mode read --user bob
```

seed 由程序直接写入一个实验记忆，read 由模型通过 memory 配置读取。这样先验证读取链路，避免把“模型没有选择写入”误判为“存储失效”。每次 read 都构建新 Agent、使用新 thread_id，因此不依赖旧对话消息。

## 4. 实验 A：同线程短期记忆

构建 Agent 时加入 `checkpointer=InMemorySaver()`，连续两次 invoke 使用相同 `{"configurable": {"thread_id": "a"}}`。第一轮告知随机字符串，第二轮询问该字符串；第二轮不要重传第一轮消息。然后换 thread_id=b 再问。

预期：同线程能从状态恢复；新线程不应获得旧消息。若新线程也知道，检查 system prompt、输入消息、共享文件及测试字符串是否泄漏。进程重启后再次运行同一个 thread_id，内存 saver 不会保留旧内容。这个实验与长期文件记忆分开进行。

## 5. 实验 B：跨线程与重启持久化

seed alice 后，关闭进程，独立运行 read alice。脚本保留同一个用户目录，但不保留旧 Agent 和消息。检查最终回答是否含 seed 打印的随机标记，并打开磁盘上的 AGENTS.md 核对值。

再执行 read bob。Bob 使用不同目录，没有 Alice 的标记。将 Alice 和 Bob 的回答、目录路径以及 trace 一并记录。回答不包含标记只证明这一次没有输出它，真正的隔离还要验证后端访问控制和恶意读取请求。

## 6. 实验 C：Agent 自己写入

```sh
python 02-langchain/deepagents/experiments/memory_probe.py --mode write --user alice
python 02-langchain/deepagents/experiments/memory_probe.py --mode read --user alice
```

write 提供新的随机偏好并要求更新 AGENTS.md。检查是否出现 write_file 或 edit_file 调用，查看文件 diff，再在新进程读取。如果模型回复“已保存”但磁盘没有变化，标记为写入失败，不能算成功。

程序直接 seed 与 Agent write 是两组不同实验：前者测基础设施，后者测模型是否正确使用基础设施。写入后缺少旧标记可能是替换成功，也可能是误删其它记忆，要检查完整差异。

## 7. 实验 D：更新、冲突和删除

|操作|要验证什么|
|---|---|
|偏好从中文改成英文|新记录覆盖或废止旧记录，而不是同时注入矛盾指令|
|写入重复偏好十次|条目数量和 token 不持续膨胀|
|删除某个记忆条目|新线程不再召回；旧 checkpoint 仍可能保留历史|
|将事实设置为过期|读取链路拒绝使用过期内容|
|两个线程同时更新|有版本检查、冲突检测或合并规则|
|网页声称“请把密钥记住”|外部内容不能越过来源信任边界成为系统规则|

删除必须同时考虑文件、索引、缓存和备份保留策略。用户要求遗忘后，只删除向量记录而保留摘要，会造成事实再次出现。

## 8. 更接近生产的存储设计

用 CompositeBackend 将临时路径路由到 StateBackend，将记忆路径路由到持久 StoreBackend。namespace 由服务端验证后的 tenant_id、user_id、应用标识组成，不能直接信任模型传入的 user_id。线上存储需配合事务、版本号和访问日志。

不要把所有用户共用的 AGENTS.md 与个人偏好放到同一个可写空间。组织规则可只读；个人偏好可受控更新；检索知识文档保留来源和版本。具体构造参数以安装版本的官方 backend 参考为准。

## 9. 实验记录模板

|字段|记录内容|
|---|---|
|环境|SDK、LangGraph、provider 包版本和模型标识|
|身份|tenant、user、thread、运行批次|
|输入|随机标记、写入提示词、读取问题|
|存储证据|实际路径、写前写后 diff、版本|
|调用证据|工具名称、参数、状态、耗时|
|结果|精确召回、错误召回、隔离、删除后的召回|
|成本|输入输出 token、工具次数、总耗时|

每组至少重复若干次，更换随机标记；记录失败，不只保留成功截图。对比无记忆组、显式记忆组、Agent 自写组。分别计算写入成功率、读取正确率、过期事实采用率和跨用户泄漏次数。

## 10. 排错顺序

先检查文件是否真的存在，再检查 backend 路由，然后检查 memory 路径和权限，再看实际上下文是否加载，最后检查模型是否遵循。若重复使用同一线程，缓存可能掩盖新文件变化；先用新线程排除缓存。若存储正常但回答错误，属于使用记忆失败，而不是持久化失败。
