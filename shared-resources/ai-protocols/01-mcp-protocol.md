# Model Context Protocol（MCP）协议精要

> **形态说明**：本篇是协议层参考（半衰期以年计），不是任何 SDK 教程（框架层不收录，理由见文末）。
> **规范基线**：2026-07-28 版（本仓基线，2026-09-16 对 modelcontextprotocol.io 官方 spec 实核；后续修订以官方为准）。

## 一、MCP 是什么

MCP 是开放协议，标准化 LLM 应用与外部数据源/工具的集成。灵感来自 LSP（语言服务器协议）：LSP 统一了编辑器↔语言工具，MCP 统一了 AI 应用↔上下文提供方。一经实现，任何 MCP Host（IDE、聊天界面、Agent）都能接入任何 MCP Server——一次集成，处处可用，这是"协议比框架稳定"的典型范例。

## 二、架构与角色

- **Host**：发起连接的 LLM 应用（如 IDE、Agent 客户端）
- **Client**：Host 内的连接器，与 Server 保持 1:1 通信
- **Server**：提供上下文与能力的服务
- 消息格式：**JSON-RPC 2.0**（UTF-8 编码）

## 三、2026-07-28 版的核心设计（相对旧版的重大变化）

1. **无状态自包含请求**：每个请求自带协议版本与能力声明（`_meta.io.modelcontextprotocol/*` 字段），取代旧版"连接级 `initialize` 握手会话"。旧版实现通过兼容矩阵（版本探测回退）互操作。
2. **服务器不再主动发起 JSON-RPC 请求**：旧版 server→client 请求（sampling/roots/elicitation 调用）已重构。现行为：server 在响应中以 `InputRequiredResult` 返回补充信息请求（如 `roots/list`），client 将结果放入 `inputResponses` 重发原请求（多轮工具请求模式 MRTR）。协议规定"服务器不发起 JSON-RPC 请求、客户端不发 JSON-RPC 响应"。
3. **能力协商下沉到每请求**：客户端能力（如 roots）在 `_meta` 中逐请求声明。

## 四、特性面

| 端 | 特性 | 说明 |
|----|------|------|
| Server | **Tools** | 供模型执行的功能（任意代码执行，须用户同意后调用） |
| Server | **Resources** | 供用户或模型使用的上下文与数据 |
| Server | **Prompts** | 面向用户的模板化消息与工作流 |
| Client | **Elicitation** | server 发起的、向用户收集补充信息的通道 |
| Client | ~~Roots~~ | **2026-07-28 起弃用**（SEP-2577）：应改用工具参数/资源 URI/配置传递目录；按特性生命周期策略保留至少 12 个月 |

通用设施：配置、进度追踪、取消、错误报告。

## 五、传输层（Binding）

协议语义与传输解耦；传输只负责消息分帧、元数据承载、取消与终止信号：

1. **stdio**：子进程标准流上的换行分隔 JSON-RPC（可靠的字节流自定义传输也应复用 stdio 分帧）
2. **Streamable HTTP**：每条消息 POST 到单一 MCP 端点；应答为 JSON 对象或**请求级 SSE 流**；可将请求元数据镜像到 HTTP 头供中间件路由（body 为准）
3. 自定义传输：必须保留 JSON-RPC 格式、消息模式、逐请求元数据模型

> 历史：旧版 HTTP+SSE 传输已被 Streamable HTTP 取代（2025-03-26 修订起）。

## 六、扩展（Extensions）

核心之外的全部扩展都是 **opt-in**，初始化时双向协商。官方扩展：

- **Tasks**：长时间运行操作的异步执行（轮询、中途输入、持久句柄）
- **Skills over MCP**：结构化 Agent 工作流指令的发现与消费
- **MCP Apps**：会话内联渲染交互式 UI（图表/表单/播放器）

## 七、安全原则（协议不能强制，实现者 SHOULD）

1. **用户同意与控制**：工具调用前必须获得明确同意；工具描述（含 annotations）视为**不可信**，除非来自可信 server
2. **数据隐私**：向 server 暴露用户数据前须取得同意，不得未经同意转传
3. **工具安全**：工具即任意代码执行路径，按对应风险对待

## 八、修订时间线

| 版本 | 要点 |
|------|------|
| 2024-11-05 | 初版（stdio + HTTP+SSE，initialize 会话） |
| 2025-03-26 | Streamable HTTP 取代 HTTP+SSE；引入授权 |
| 2025-06-18 | sampling/elicitation 等客户端特性细化 |
| **2026-07-28（本仓基线）** | 无状态重构：逐请求元数据/能力协商；server 不再主动发起 JSON-RPC（MRTR 模式）；Roots 弃用；官方扩展体系 |

## 九、模式不变量（框架无关）

- 协议价值 = N×M 集成问题降为 N+M：Server 实现一次，所有 Host 可用
- 工具调用永远经用户同意闸门——任何 Host 实现不应绕过
- 能力必须协商，不做隐式假设（无协商即无该能力）
- 传输可替换，语义不变：业务代码不应感知 stdio vs HTTP

## 框架层说明

TypeScript/Python/Rust/Kotlin SDK、FastMCP 等实现层**不在本仓收录范围**（过时风险高，框架竞争未收敛）。需要 SDK 用法时以官方 modelcontextprotocol.io 与各 SDK 文档为准；本篇只沉淀协议与模式层。

## 相关

- [02-agent-patterns.md](./02-agent-patterns.md) — Agent 模式语言（MCP 是工具接入的协议标准）
- 官方规范：<https://modelcontextprotocol.io/specification/2026-07-28>
