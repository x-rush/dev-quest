# flag - 命令行参数解析

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

flag 是标准库的命令行参数解析器：声明式注册 `-name value` 风格的参数，`flag.Parse()` 一次完成解析与类型转换。心智模型——**每个 flag 是一个已绑定变量的注册项**；注册函数返回绑定变量的指针，或直接绑定已有变量（`*IntVar`）。`flag.Args()` 返回解析后剩余的位置参数。

## 📖 语法 / 签名

```go
// 注册 + 解析
port := flag.Int("port", 8080, "监听端口")          // 返回 *int
verbose := flag.Bool("verbose", false, "详细输出")   // bool 可省略值：-verbose
name := flag.String("name", "", "服务名")
flag.IntVar(&cfg.Retry, "retry", 3, "重试次数")     // 绑定已有变量
flag.Parse()                                       // 之后才能读

// 解析后取值
fmt.Println(*port, *verbose)
flag.Args()      // 位置参数 []string（非 - 开头的剩余部分）
flag.Arg(0)      // 第 n 个位置参数
flag.NArg(); flag.NFlag()

// 语义细节
// -port=9000 / -port 9000 / --port 9000 均可（单双横线等价）
// bool 特殊：-verbose 即 true，-verbose=false 才能显式传假值
// -port 后跟位置参数时：-port 9000 合法，flag 消费下一个非 flag 词
```

**自定义 flag.Value**：实现 `String() string` 与 `Set(string) error` 两方法的类型即可注册——适合列表参数、枚举校验、时间区间等复合值。

**子命令模式**：`flag.NewFlagSet(name, flag.ExitOnError)` 为每个子命令建独立集合，手动按 `os.Args[1]` 分发；k8s/docker 风格 CLI 的标准骨架（不需要第三方库时的最小实现）。

## 💡 示例

```go
package main

import (
	"flag"
	"fmt"
	"strings"
)

// 自定义 Value：-tags a,b,c 解析为切片
type stringList []string

func (s *stringList) String() string { return strings.Join(*s, ",") }

func (s *stringList) Set(v string) error {
	for _, part := range strings.Split(v, ",") {
		*s = append(*s, strings.TrimSpace(part))
	}
	return nil
}

func main() {
	// 1. 基础注册与解析
	port := flag.Int("port", 8080, "监听端口")
	verbose := flag.Bool("verbose", false, "详细输出")
	var retry int
	flag.IntVar(&retry, "retry", 3, "重试次数")

	var tags stringList
	flag.Var(&tags, "tags", "逗号分隔标签")

	flag.Parse()

	fmt.Println(*port, *verbose, retry, tags.String())
	fmt.Println("位置参数:", flag.Args())
}
```

运行实测（go1.25.14）：`./prog -port=9000 -verbose -tags "a, b" pos1 pos2` → `9000 true 3 a,b` + `位置参数: [pos1 pos2]`（tags 打印的是自定义 `String()` 的逗号连接，不是切片格式）。

**子命令骨架**：

```go
func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "用法: prog <serve|migrate> [flags]")
		os.Exit(2)
	}
	switch os.Args[1] {
	case "serve":
		fs := flag.NewFlagSet("serve", flag.ExitOnError)
		addr := fs.String("addr", ":8080", "监听地址")
		fs.Parse(os.Args[2:])
		runServe(*addr)
	case "migrate":
		fs := flag.NewFlagSet("migrate", flag.ExitOnError)
		dir := fs.String("dir", "up", "迁移方向")
		fs.Parse(os.Args[2:])
		runMigrate(*dir)
	default:
		os.Exit(2)
	}
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：`flag.Parse()` 之前读 flag 指针。
- ✅ **正确做法**：Parse 之后所有绑定变量才有用户值；注册顺序无关，解析按名匹配。
- ❌ **错误做法**：`-verbose false` 想传布尔假值。
- ✅ **正确做法**：bool flag 不消费下一个词——`false` 会变成位置参数；必须写 `-verbose=false`。
- ❌ **错误做法**：混合位置参数与 flags，期望 flag 自动跳过。
- ✅ **正确做法**：遇到第一个位置参数后 flag 停止解析（后续 `-x` 也进 `flag.Args()`）；约定用户把 flags 放最前，或自己用 NewFlagSet 分段解析。
- ❌ **错误做法**：flag.Value 的 Set 返回 nil 但内部没校验。
- ✅ **正确做法**：Set 负责自定义值转换，可拒绝非法格式；Parse 后还要校验业务范围与参数组合。错误后是返回、退出还是 panic 取决于 FlagSet 的错误处理模式；String 也可被调用者直接使用，不仅用于帮助文本。
- ❌ **错误做法**：子命令直接 `flag.Parse()` 复用默认集合。
- ✅ **正确做法**：每个子命令用 `flag.NewFlagSet` 独立集合；`flag.ExitOnError` 出错自动退出，`ContinueOnError` 由代码接管。
- ❌ **错误做法**：默认 flag 包的错误输出与 usage 无法定制。
- ✅ **正确做法**：`flag.CommandLine.SetOutput(w)`、`flag.Usage = func(){}` 可整体接管；或自建 FlagSet 设置同名字段。

<!-- full-library-explanation -->
## 把参数解析做成可测试的输入边界

前置是指针、错误返回值与 os.Args。注册 flag 只是为名称绑定存储位置和转换规则，不检查所有业务约束。flag.Int 能解析 -1，但重试次数可能要求非负；两个参数之间的依赖也应在 Parse 成功后统一验证。默认值应该可解释，例如超时不能静默采用零而导致无限等待。

可测试的命令入口通常为每次调用创建 FlagSet，使用 ContinueOnError，接收 []string 并返回配置和错误，让最外层 main 决定退出码。这样测试不用修改全局 os.Args，也不会因 ExitOnError 直接结束整个测试进程。SetOutput 可将帮助文本写入缓冲区，验证错误反馈是否包含可用参数。

练习：分别解析 `-port 9000 file.txt`、`file.txt -port 9000` 和 `-verbose false`。第一项 port 为 9000、位置参数只有 file.txt；第二项从 file.txt 起都成为位置参数，port 保持默认；第三项 verbose 为 true，而 false 是位置参数。再为 0 和 65536 端口增加明确的业务校验测试。自定义 Set 若追加切片，应说明重复传入 -tags 是累加还是覆盖，避免用户只能试错发现规则。

## 🔗 相关条目

- 📄 **[os 包](./11-os.md)** - os.Args 原始参数与 Exit 语义
- 📄 **[strconv 包](./14-strconv.md)** - flag 内部的类型转换器
- 📄 **[net/http 包](./03-net-http.md)** - 命令行入口启动 HTTP 服务
- 📄 **[log/slog 包](./15-log-slog.md)** - verbose flag 调日志级别
- 🌐 **[pkg.go.dev/flag](https://pkg.go.dev/flag)** - 官方文档
- 🌐 **[pkg.go.dev/flag 官方示例（自定义 Value）](https://pkg.go.dev/flag#pkg-examples)** - flag.Value 示例

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
