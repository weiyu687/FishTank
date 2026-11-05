# Deep Agents：架构、默认工具与扩展方式

本文讨论 LangChain 的 `deepagents` Python SDK，不是泛指所有深度研究 Agent。文档核对日期：2026-11-05。接口变化较快，学习时保存依赖版本，不能把 SDK、CLI 和托管平台的默认配置混为一谈。

[TOC]

## 学习路线

1. 阅读本篇，理解 Agent 循环与内置能力。
2. 阅读[记忆机制与实验](02-memory-lab.md)，动手做对照实验。
3. 阅读[Skills、工具与工程化](03-engineering.md)，组织自己的应用。
4. 使用[面试专栏](../../04-agent-interview/01-foundations.md)检查是否能解释设计取舍。

## 1. 三层架构如何区分

|层|承担的职责|何时直接使用|
|---|---|---|
|LangChain|模型、工具、消息、Agent 循环与中间件|常规工具调用应用|
|LangGraph|状态图、执行恢复、持久化、中断和流式运行|流程需要精确控制|
|Deep Agents|在上述能力上组合文件上下文、子任务、记忆和 Skills|长任务、资料整理、代码与研究类应用|

Deep Agents 不是换了一个更聪明的模型，而是给模型配置工作环境。模型负责提出调用，运行时执行工具并把结果交回模型。最终可靠性仍受模型、工具契约、数据质量、预算和验证机制共同约束。[官方架构说明](https://www.langchain.com/oss-overview)

## 2. “默认插件”实际上包括哪些东西

在 SDK 中，更准确的术语是工具、middleware、backend 与 skill。工具是模型可请求的动作；middleware 处理调用前后行为；backend 决定文件落在哪里；skill 是按任务加载的流程知识。

|能力|模型可见入口|启用条件与边界|
|---|---|---|
|文件导航|ls、glob、grep|通过配置的文件后端操作|
|读取与修改|read_file、write_file、edit_file|读写权限仍需在运行时限制|
|删除|delete|当前文档标注 deepagents ≥ 0.7，且后端支持|
|子任务委派|task|子 Agent 的上下文和工具需要单独设计|
|命令执行|execute|需支持执行的后端；普通内存文件系统不等于 shell|
|任务清单|write_todos|当前工具文档要求显式加入 TodoListMiddleware|
|长期说明加载|memory 参数|指定文件及合适的存储后端|
|按需流程加载|skills 参数|提供含 SKILL.md 的目录|

不要把浏览器、互联网搜索、数据库、邮件或任何 MCP 服务当成默认已经连接的插件。它们需要业务方提供工具和授权。工具名存在也不代表后端拥有相应权限。[官方工具清单](https://docs.langchain.com/oss/python/deepagents/tools)

## 3. 中间件的作用

FilesystemMiddleware 连接文件工具与后端；SubAgentMiddleware 提供任务委派；MemoryMiddleware 加载指定的记忆文件；SkillsMiddleware 提供流程知识的渐进加载。摘要能力用于控制上下文长度，大型工具输出也可以外置到文件后再按需读取。

要区分“框架提供这个组件”和“某次构建确实启用了它”。model、参数、profile 和 SDK 版本可能影响最终配置。排错时查看实际工具调用轨迹与安装版本，而不是只看博客中的截图。[中间件参考](https://reference.langchain.com/python/deepagents/middleware)

### 覆盖默认中间件时的陷阱

当前文档允许用同名中间件实例替换默认实例。替换不是参数合并：自定义 FilesystemMiddleware 需要自己带好 backend 等配置。不要认为 create_deep_agent 外层传入的每个参数都会自动传给替换实例。摘要阈值也需要根据任务长度和模型窗口设计。[自定义指南](https://docs.langchain.com/oss/python/deepagents/customization)

## 4. 最小应用

使用独立 Python 3.11+ 环境，并核对所选包版本的 Requires-Python。安装 `deepagents` 和模型供应商集成包，例如 `langchain-openai`。模型名称由环境变量传入，避免教程绑定某个付费模型。

```python
import os
from deepagents import create_deep_agent

def lookup_policy(topic: str) -> str:
    """查询演示知识库的指定主题；未知主题明确返回未找到。"""
    policies = {"refund": "演示规则：未发货订单可申请取消。"}
    return policies.get(topic, "未找到对应规则，请补充主题。")

agent = create_deep_agent(
    model=os.environ["DEEPAGENT_MODEL"],
    tools=[lookup_policy],
    system_prompt="你是演示知识助手。规则问题必须调用工具；信息不足时明确说明。",
)
result = agent.invoke({"messages": [{"role": "user", "content": "refund 有什么规则？"}]})
print(result["messages"][-1].content)
```

环境变量可设为供应商支持的 `provider:model` 标识，同时在本地设置相应密钥。不要把密钥写入代码或提交到 Git。这个例子只查询本地字典，调用语言模型仍可能产生费用。

观察重点：模型是否选择正确工具、参数是否正确、未找到时是否编造、最终回答是否忠于工具结果。一次成功只能证明路径跑通，不能证明整个应用可靠。

## 5. Backend 如何选

|后端|典型用途|必须验证的边界|
|---|---|---|
|StateBackend|线程内草稿与临时文件|跨调用依赖状态保存；不天然跨线程共享|
|FilesystemBackend|本地实验、挂载卷文件|持久卷生命周期、路径和租户隔离|
|StoreBackend|跨线程共享的数据|底层 store 是否真持久化、namespace 是否隔离|
|CompositeBackend|临时区与记忆区分离|路由前缀是否指向预期存储|
|Sandbox 后端|运行代码和命令|网络、资源、文件、凭证边界|

backend 是存储或执行实现，不是记忆算法。把文件写到持久目录不会自动完成事实去重、冲突消解和过期管理。LocalShellBackend 直接在宿主机执行；不能因为路径设置了根目录就认为 shell 被安全隔离。[后端指南](https://docs.langchain.com/oss/python/deepagents/backends)

## 6. 什么时候不需要 Deep Agents

字段提取、固定 SQL 查询或三步审批流程，通常直接使用结构化输出或固定工作流更容易验证。只有任务确实需要动态拆解、反复检索和上下文整理时，再引入完整 Agent 能力。评估时对比同一任务集的成功率、总成本、尾延迟和人工接管率。
