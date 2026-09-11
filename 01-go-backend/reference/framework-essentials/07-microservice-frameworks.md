# 微服务框架选型：go-zero vs Kratos vs Kitex

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

Go 后端的主流工程路线有两种：

- **组装派（本模块主线）**：Gin/chi + GORM/sqlc + 标准库 + 独立中间件，按需自由组合。框架层薄，决策权在开发者。
- **一体化微服务框架**：框架自带脚手架、代码生成、RPC、限流熔断、监控埋点，用"约定 + 工具链"换一致性。代表：go-zero、Kratos；Kitex 则是其中聚焦 RPC 层的高性能代表。

解决的问题：**当服务从单体走向多服务，"自由组装"的一致性成本上升时，是否值得让渡一部分自由度换取框架级的工程规范**。

## 📊 对比表

| 维度 | go-zero | Kratos | Kitex |
|------|---------|--------|-------|
| **出品方** | 好未来开源，CNCF 收录，国内使用广 | B 站开源 | 字节跳动 CloudWeGo 生态 |
| **定位** | 一体化微服务框架（HTTP+RPC+任务） | gRPC 中心的微服务工程框架 | 高性能 RPC 框架（非全栈） |
| **开发范式** | `.api` DSL / proto → goctl 一条龙生成服务骨架、model、client | Protobuf 为 IDL 中心，Wire 依赖注入，transport/business/data 分层 | thrift/protobuf 定义 IDL → 生成 client/server 代码 |
| **代码生成** | 重度：api/rpc/model 全覆盖（goctl） | 中度：proto 生成 + 脚手架 | 重度：RPC 层强类型生成 |
| **内置治理** | 限流、熔断、降级、缓存、监控开箱即用 | 中间件生态 + 可插拔治理组件 | 治理能力以扩展模块提供（连接池、负载均衡、熔断） |
| **HTTP 支持** | 内置（api 服务直接对外） | gRPC 为主，HTTP 网关化处理 | 不内置，配套 Hertz（同属 CloudWeGo） |
| **学习曲线** | 主要在 goctl 工作流与约定 | 主要在分层规范与生态组件 | 主要在 thrift/IDL 与扩展机制 |
| **绑定程度** | 高：服务结构、目录、配置强约定 | 中高：分层与生命周期强约定 | 低：只绑定 RPC 层，其余自由组装 |
| **典型适用** | 团队想要"一条命令生成一套微服务"的统一工作流 | gRPC 优先、重视工程分层规范的中大型团队 | 极致 RPC 性能与高并发场景（可保留现有技术栈） |

## 💡 示例

**go-zero：一个 `.api` 文件生成整条服务链**

```api
// user.api（go-zero 的输入）
type UserReq struct {
    Id int64 `path:"id"`
}

type UserReply struct {
    Name string `json:"name"`
}

@server (
    prefix: /api
)
service user-api {
    @handler getUser
    get /user/:id (UserReq) returns (UserReply)
}
```

```bash
goctl api go -api user.api -dir .   # 生成 handler/logic/types/路由注册全套骨架
```

**组装派等价物（本模块主线做法）**：`Gin` 注册路由 + 手写 handler/service/model 分层——灵活但一致性靠团队约定。

## 🧭 选型建议

| 场景 | 推荐 | 理由 |
|------|------|------|
| 单体或少量服务，团队小 | 组装派（Gin+GORM/sqlc） | 一致性成本尚低，自由组装收益最大 |
| 服务数量增长、要统一工作流 | go-zero | goctl 一条龙最大化降低协作分歧 |
| gRPC 优先、强调工程分层规范 | Kratos | 分层与生命周期约定清晰，适合中大型团队 |
| RPC 性能敏感、不想绑定全栈框架 | Kitex | 只替换 RPC 层，HTTP/存储仍可用现有组合 |
| 学习目的（掌握通用微服务概念） | 组装派起步 | 先理解中间件/RPC/治理的手工形态，再评估框架收益 |

一句话结论：**组装派与一体化框架之争本质是"自由度 vs 一致性"的权衡；go-zero 换工作流统一，Kratos 换分层规范，Kitex 只换 RPC 性能。三者都值得"读懂"，是否"采用"取决于团队规模与服务数量。**

## ⚠️ 常见陷阱

- ❌ **错误做法**：把一体化框架的代码生成产物当黑盒直接手改。
- ✅ **正确做法**：业务逻辑写在框架预留的扩展点（go-zero 的 logic、Kratos 的 business 层），重新生成不覆盖。
- ❌ **错误做法**：小团队、两三个服务就引入一体化框架。
- ✅ **正确做法**：框架一致性收益在服务数量与人多了之后才显现，早期组装派更轻。
- ❌ **错误做法**：选框架只看性能榜单。
- ✅ **正确做法**：绑定程度、工作流迁移成本、团队认知负担才是长期成本。

## 🔗 相关条目

- 📄 **[sqlc vs GORM vs ent](./03-sqlc-vs-gorm.md)** - 数据层选型（一体化框架之外的数据访问自由度）
- 📄 **[路由器选型对比](./04-router-selection.md)** - 组装派的 Web 层选型
- 📄 **[Gin 框架速查](./01-gin-framework.md)** - 本模块主线框架
- 📄 **[微服务设计](../../advanced-topics/architecture/01-microservices-design.md)** - 架构解释层
- 🌐 **[go-zero 官方文档](https://go-zero.dev/)** - 权威来源
- 🌐 **[Kratos 官方文档](https://go-kratos.dev/)** - 权威来源
- 🌐 **[CloudWeGo（Kitex/Hertz）](https://www.cloudwego.io/zh/)** - 权威来源

---

*最后更新: 2026年09月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
