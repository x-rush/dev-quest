# log/slog - 结构化日志

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

slog（Go 1.21+）是标准库的**结构化日志**包：日志是"消息 + 键值属性对"而非拼接字符串，机器可检索、可聚合。心智模型——**Logger（发日志）→ Handler（决定格式）→ Level（决定取舍）** 三件套；`slog.Info` 等包级函数走 Default Logger，业务代码通常自己持有 `*slog.Logger` 注入。

## 📖 语法 / 签名

```go
// 快捷函数：级别 + 消息 + 键值对（键 string，值 any，交替排列）
slog.Info("request done", "method", "GET", "path", "/health")
slog.Warn("slow", "ms", 950)
slog.Error("db down", "err", err)
slog.Debug("trace detail", "k", v)   // 默认级别 Info，Debug 被丢弃

// Logger 对象：带上下文与来源
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelDebug,             // 全局最低级别
    AddSource: true,                    // 记录调用位置
}))
logger = logger.With("service", "api")  // 预置公共属性，返回新 Logger
logger = logger.WithGroup("http")       // 分组：后续属性嵌套在 "http" 下

// 显式 Attr 形式（值类型明确）
logger.LogAttrs(ctx, slog.LevelInfo, "msg", slog.String("k", "v"), slog.Int("n", 1))

// 与 log 包兼容桥
slog.SetDefault(slog.New(slog.NewJSONHandler(os.Stdout, nil)))
log.Println("旧代码走的也变成 JSON") // log 输出被 slog 接管
```

**核心类型**：

| 类型 | 职责 |
|------|------|
| `Logger` | 发日志的入口，并发安全，值语义可随意复制/With 派生 |
| `Handler` | 格式化器：内置 `TextHandler`（key=value）与 `JSONHandler`；自定义即实现 `Handle/Enabled/WithAttrs/WithGroup` |
| `Level` | Debug(-4) < Info(0) < Warn(4) < Error(8)，可自定义数值 |
| `Attr` | `slog.String/Int/Bool/Time/Duration/Any(...)` 构造的键值对 |
| `Record` | 一条日志的载体，Handler.Handle 的入参 |

**性能约定**：`logger.Debug(...)` 的键值对在级别被禁用时也会构造参数（开销小但不为零）；重路径用 `logger.LogAttrs(ctx, level, msg, attrs...)` 或 `logger.Enabled(ctx, level)` 预判。

## 💡 示例

```go
package main

import (
	"errors"
	"log/slog"
	"os"
)

func main() {
	// 1. JSON Handler：结构化输出的默认选择
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	})).With("service", "api")

	logger.Info("request done", "method", "GET", "path", "/health", "status", 200)
	// {"time":"2026-09-14T12:00:00+08:00","level":"INFO","msg":"request done",
	//  "service":"api","method":"GET","path":"/health","status":200}

	// 2. 级别过滤：低于设定级别的被丢弃
	logger.Debug("这条会出现（Handler 级别是 Debug）")
	slog.SetLogLoggerLevel(slog.LevelInfo) // 包级快捷函数的默认级别
	slog.Info("包级函数走 default logger")

	// 3. WithGroup：属性分组嵌套
	reqLog := logger.WithGroup("http")
	reqLog.Warn("slow", "ms", 950)
	// ..."http":{"ms":950}

	// 4. 错误入日志：err 键是惯例
	dbErr := errors.New("connection refused")
	logger.Error("db query failed", "err", dbErr)
}
```

**TextHandler 输出对比**：`time=2026-09-14T12:00:00.000+08:00 level=INFO msg="request done" service=api method=GET`——人类可读，机器同样可解析；开发环境用 Text，生产采集用 JSON。

## ⚠️ 常见陷阱

- ❌ **错误做法**：`slog.Info(fmt.Sprintf("user %d did %s", id, action))` 拼消息。
- ✅ **正确做法**：`slog.Info("user action", "id", id, "action", action)`——键值对才能被日志系统按字段检索与聚合。
- ❌ **错误做法**：键值成对交替记错位置。
- ✅ **正确做法**：`slog.Info("msg", "k1", v1, "k2", v2)`——键必须是 string，配错编译不报错但日志畸形；易错场景改用 `LogAttrs + slog.Int(...)` 系列构造器（编译期可查）。
- ❌ **错误做法**：以为 `slog.Debug` 不输出是 Handler 出 bug。
- ✅ **正确做法**：Default Logger 级别为 Info，Debug 被丢弃；调级别用 HandlerOptions.Level 或 `slog.SetLogLoggerLevel`。
- ❌ **错误做法**：期望不同模块有不同级别却只有一个 Handler。
- ✅ **正确做法**：按模块构造不同 Handler/Logger 注入；Handler 的 Enabled 是逐条日志的开关。
- ❌ **错误做法**：自己维护全局 logger 变量到处 import。
- ✅ **正确做法**：Logger 显式注入（struct 字段或参数）；包级 `slog.Default` 仅限 main/胶水层。
- ❌ **错误做法**：日志里塞敏感字段（token、密码、身份证号）。
- ✅ **正确做法**：入日志前脱敏；或实现自定义 Handler 统一过滤黑名单键。

## 🔗 相关条目

- 📄 **[net/http 包](./03-net-http.md)** - 请求日志中间件
- 📄 **[context 包](./05-context.md)** - ctx 携带请求级 logger 的传递链
- 📄 **[errors 标准库](./09-errors.md)** - err 字段的最佳载体
- 📄 **[os 包](./11-os.md)** - 输出目标 os.Stdout/os.Stderr
- 🌐 **[pkg.go.dev/log/slog](https://pkg.go.dev/log/slog)** - 官方文档
- 🌐 **[Structured Logging with slog（官方博客）](https://go.dev/blog/slog)** - 设计说明

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
