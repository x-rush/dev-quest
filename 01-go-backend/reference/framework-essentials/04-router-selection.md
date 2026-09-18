# Gin vs chi vs echo：Go HTTP 路由器选型

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

Go 生态中三个最常被对比的 HTTP 路由/框架方案：

- **Gin**：自带上下文（`gin.Context`）与中间件链的**全功能 Web 框架**，生态最庞大，是本模块 `frameworks/` 的主修框架。
- **chi**：**与 `net/http` 标准库完全兼容**的轻量路由器，只做路由与中间件调度，其余交给标准库。
- **echo**：**极简高性能 Web 框架**，API 设计克制，内置合理默认值。

解决的问题：**新服务的第一行代码该 `go get` 谁**——在框架便利性与标准库兼容性之间做权衡。

## 📊 对比表

| 维度 | Gin | chi | echo |
|------|-----|-----|------|
| **定位** | 全功能框架（路由+绑定+渲染+中间件生态） | 极简路由器（补齐 `net/http` 的路由短板） | 极简框架（路由+上下文+中间件，少即是多） |
| **处理函数签名** | `func(c *gin.Context)`（自有 Context） | `func(w http.ResponseWriter, r *http.Request)`（原生签名） | `func(c echo.Context) error`（自有 Context） |
| **标准库兼容性** | 中：`gin.Context` 包裹了 Request/Writer，与原生中间件混用需适配 | **完全兼容**：http.Handler 与 func(http.Handler) http.Handler 形式的中间件可组合；标准库没有 http.Middleware 类型 | 中：自有 Context，需经适配器使用原生组件 |
| **路径参数语法** | `/users/:id` | `/users/{id}` | `/users/:id` |
| **性能心智** | 基于高效路由树，同级别中表现优秀 | 接近标准库开销，路由树高效 | 与 Gin 同一梯队，差异在实际业务中可忽略 |
| **中间件生态** | 最丰富（社区贡献大量现成中间件） | 复用整个标准库中间件生态 | 内置常用中间件，社区规模小于 Gin |
| **请求绑定/校验** | 内置 `ShouldBind*` 多格式绑定 | 无（自行用 `encoding/json` 等处理） | 内置绑定与校验支持 |
| **学习曲线** | 低（文档与示例最多） | 最低（懂 `net/http` 就已会 chi） | 低（API 面小） |
| **迁移自由度** | 较低（业务代码与 gin.Context 耦合） | **最高**（业务层可保持独立；路由注册与参数提取仍需适配） | 较低（echo.Context 耦合） |
| **何时选它** | 需要开箱即用的全家桶与最大社区支持 | 已有标准库代码资产、重视长期可移植性 | 喜欢小 API 面与显式错误返回风格 |

## 💡 示例

同一个「带中间件的路径参数路由」在三者中的写法：

```go
// Gin：自有 Context，绑定+响应一体
r := gin.Default()                       // 自带 Logger/Recovery 中间件
r.GET("/users/:id", func(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{"id": c.Param("id")})
})
r.Run(":8080")
```

```go
// chi：原生 http.Handler，标准库组件直接挂载
r := chi.NewRouter()
r.Use(middleware.Logger)                 // chi 官方中间件，也可用任意 http.Handler 中间件
r.Get("/users/{id}", func(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    json.NewEncoder(w).Encode(map[string]string{"id": id})
})
http.ListenAndServe(":8080", r)
```

```go
// echo：显式返回 error 的风格
e := echo.New()
e.Use(middleware.Logger())
e.GET("/users/:id", func(c echo.Context) error {
    return c.JSON(http.StatusOK, map[string]string{"id": c.Param("id")})
})
e.Start(":8080")
```

## 🧭 选型建议

| 场景 | 推荐 | 理由 |
|------|------|------|
| 新项目、团队要统一技术栈、要现成中间件 | Gin | 生态最大，招人与查资料成本最低 |
| 存量代码基于 `net/http`，只想补路由能力 | chi | 零侵入，逐步引入 |
| 长期项目、重视框架可替换性 | chi | 业务代码不与框架类型耦合 |
| 追求极小依赖面与显式错误处理 | echo | API 面小、`return err` 风格统一 |
| 学习 Go Web 的第一站 | chi 或 Gin | chi 贴近标准库本质；Gin 贴近工业界主流 |
| 微服务间技术栈统一（本模块实战项目） | Gin | 与模块教程、示例保持一致 |

一句话结论：**要生态选 Gin，要标准库与可移植性选 chi，要极简选 echo；三者性能都在同一梯队，选型应优先看团队约定与代码耦合策略，而非跑分。**

## ⚠️ 常见陷阱

- ❌ **错误做法**：因为某框架"跑分快"就更换现有项目的路由器。
- ✅ **正确做法**：先测量路由层在当前真实负载中的占比，迁移成本与生态匹配才是决定因素。
- ❌ **错误做法**：在 Gin/echo 项目里直接安装 `net/http` 风格中间件并期待生效。
- ✅ **正确做法**：使用框架自身的中间件签名，或经适配器转换；反之 chi 可直接吃标准库中间件。
- ❌ **错误做法**：混用 `:id` 与 `{id}` 两种参数语法。
- ✅ **正确做法**：记住规则——Gin/echo 用 `:id`，chi 与标准库 `http.ServeMux` 风格一致用 `{id}`。
- ❌ **错误做法**：把业务逻辑写在路由处理函数里，导致框架类型渗透到领域层。
- ✅ **正确做法**：handler 只做绑定与响应，业务逻辑下沉到与框架无关的 service 包。

<!-- full-library-explanation -->
## 先实现协议边界，再比较框架便利性

前置是 http.Handler、中间件和 context。路由器主要把方法与路径映射到处理函数；请求绑定只是把输入转换成 Go 值，不能证明用户有权操作这个资源。无论使用哪个框架，都要在业务边界检查对象归属、设置请求体上限、传递取消信号、映射错误，并为服务器配置读写超时。

选择时先建立三个小端点：GET /users/{id}、POST /users、GET /health。以同一组测试检查未知路由、错误方法、非法 JSON、缺少认证和正常响应。比较中间件如何读取与改写状态、错误如何返回、路径参数如何传递到业务函数，而不是只测空 Handler 的路由吞吐。Go 1.22 起标准 ServeMux 已支持方法和通配符，小服务也应把它作为比较基线。

练习：业务函数只接收 context.Context、用户 id 和必要接口，将同一函数接到 Gin 与标准库 Handler。若替换框架需要重写业务规则，说明边界仍耦合框架类型。chi 保留标准签名，但 chi.URLParam 仍是具体路由器 API，因此迁移时处理路径参数的适配层仍需调整。Echo 的具体类型签名按主版本核对，本页片段采用 v4 风格，不能与其他主版本直接混用。

## 🔗 相关条目

- 📄 **[Gin 框架速查](./01-gin-framework.md)** - 主修框架的完整字典
- 📄 **[sqlc vs GORM 选型](./03-sqlc-vs-gorm.md)** - 同系列的数据层选型条目
- 📄 **[Gin 框架基础教程](../../frameworks/01-gin-framework-basics.md)** - 操作指南层
- 📄 **[Go 标准库核心 API](../library-guides/01-go-standard-library.md)** - `net/http` 原生路由与中间件
- 🌐 **[chi 官方仓库](https://github.com/go-chi/chi)** - 权威来源
- 🌐 **[echo 官方文档](https://echo.labstack.com/)** - 权威来源

---

*最后更新: 2026年09月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
