# strconv - 字符串与基本类型互转

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

strconv 负责**字符串与基本类型（整型/浮点/布尔）之间的高性能转换**。与 `fmt.Sprintf` 的关系：strconv 表达单个基本值的转换，fmt 适合复合格式；热路径可测量 Append 系列是否减少分配。SQL 使用参数化查询，CSV 使用 encoding/csv，不靠手工拼接完成转义。

## 📖 语法 / 签名

```go
// 解析：string → 类型（失败返回 *NumError）
strconv.Atoi("42")                    // (int, err)：ParseInt 的 int 快捷方式
strconv.ParseBool("true")             // 1/t/T/TRUE/true/True 与 0/f/F/FALSE/false/False
strconv.ParseInt("-42", 10, 64)       // (int64, err)：进制 + 位宽
strconv.ParseUint("42", 10, 32)       // 无符号
strconv.ParseFloat("3.14", 64)        // (float64, err)：位宽 32/64

// 格式化：类型 → string
strconv.Itoa(42)                      // "42"
strconv.FormatInt(-42, 16)            // "-2a"（指定进制）
strconv.FormatFloat(3.14, 'f', 2, 64) // "3.14"：格式符 + 精度 + 位宽
strconv.FormatBool(true)              // "true"

// Append：追加到已有 []byte；容量足够时可减少分配
buf = strconv.AppendInt(buf, 42, 10)
buf = strconv.AppendQuote(buf, s)     // 带 Go 字面量引号转义

// 引号处理
strconv.Quote("he\"llo")              // "\"he\\\"llo\""：加引号+转义
strconv.Unquote(`"hello"`)            // 去 Go 字面量引号
```

**FormatFloat 格式符**：`'f'`（无指数，如 3.14）、`'e'/'E'`（科学计数）、`'g'`（自动选择，与 `%g` 一致）、精度 -1 表示"最短能还原的表示"。

**错误类型 NumError**：解析失败返回 `*strconv.NumError`，字段 `Func`（"Atoi"等）、`Num`（原始输入）、`Err`（`ErrSyntax` 语法错 / `ErrRange` 超出位宽范围）——可用 `errors.Is(err, strconv.ErrRange)` 判别。

## 💡 示例

```go
package main

import (
	"errors"
	"fmt"
	"strconv"
)

func main() {
	// 1. 解析族
	n, err := strconv.Atoi("42")
	fmt.Println(n, err) // 42 <nil>

	b, _ := strconv.ParseBool("TRUE")
	fmt.Println(b) // true

	i64, _ := strconv.ParseInt("ff", 16, 64) // 按 16 进制解析
	fmt.Println(i64)                         // 255

	f, _ := strconv.ParseFloat("3.14", 64)
	fmt.Println(f) // 3.14

	// 2. NumError 双形态判别
	_, err = strconv.Atoi("abc") // 语法错
	var ne *strconv.NumError
	errors.As(err, &ne)
	fmt.Println(ne.Err == strconv.ErrSyntax) // true

	_, err = strconv.ParseInt("99999999999999999999", 10, 32) // 超范围
	fmt.Println(errors.Is(err, strconv.ErrRange))             // true

	// 3. 格式化族
	fmt.Println(strconv.Itoa(-7))                          // -7
	fmt.Println(strconv.FormatInt(255, 16))                // ff
	fmt.Println(strconv.FormatFloat(3.14159, 'f', 2, 64))  // 3.14
	fmt.Println(strconv.FormatFloat(3.14159, 'g', -1, 64)) // 3.14159

	// 4. Append 复用缓冲区拼接
	buf := make([]byte, 0, 32)
	buf = append(buf, "id="...)
	buf = strconv.AppendInt(buf, 9001, 10)
	buf = append(buf, ",ok="...)
	buf = strconv.AppendBool(buf, true)
	fmt.Println(string(buf)) // id=9001,ok=true

	// 5. 引号
	fmt.Println(strconv.Quote("say \"hi\"\n")) // "say \"hi\"\n"
	uq, err := strconv.Unquote(`"line\ttwo"`)
	fmt.Println(uq, err == nil) // line	two true
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：`strconv.Atoi` 忽略错误直接用返回值。
- ✅ **正确做法**：解析族（Atoi/Parse*）失败返回 `*NumError`，数值返回值可能是零、范围边界值或无穷大，必须处理 err；这是外部输入（env/flag/HTTP 参数）的必经校验点。
- ❌ **错误做法**：用 `fmt.Sprintf("%d", x)` 拼接热路径。
- ✅ **正确做法**：单值转换可用 `strconv.Itoa/AppendInt`；fmt 适合复合格式化。性能与分配收益用真实输入测量，不能仅凭 API 名保证。
- ❌ **错误做法**：`Atoi` 期望解析 int64 超范围值成功。
- ✅ **正确做法**：Atoi 等价 ParseInt(s, 10, 0)（平台位宽）；大数/指定位宽用 `ParseInt(s, base, 64)` 并检查 `ErrRange`。
- ❌ **错误做法**：ParseInt 进制参数传 0 想当然。
- ✅ **正确做法**：base=0 是"按前缀识别"（0x/0b/0o/0 前缀，下划线分隔符合法），base 显式 10 时纯数字——两者行为不同，选对语义。
- ❌ **错误做法**：Unquote 直接解用户原始 JSON 字符串。
- ✅ **正确做法**：Unquote 只认 **Go 字面量**规则；JSON 字符串交给 encoding/json。
- ❌ **错误做法**：Append 系列忘记接收返回值（`strconv.AppendInt(buf, ...)` 孤立调用）。
- ✅ **正确做法**：`buf = strconv.AppendInt(buf, ...)`——append 语义，可能扩容换底层数组。

<!-- full-library-explanation -->
## 转换通过不等于输入可接受

前置是数字类型与 error。外部输入先按指定语法转换，再验证业务范围。例如 ParseUint(text,10,16) 拒绝负数和超过 65535 的值，但仍接受 0；作为服务监听端口时，0 表示由系统分配端口，是否允许必须由产品约定决定。ParseFloat 还接受 NaN 和无穷大，如果后续计算要求有限数，需要用 math.IsNaN 与 math.IsInf 拒绝它们。

数值转换出错后不要继续使用返回数值。ErrRange 时 ParseInt 可能返回对应边界值，ParseFloat 可能返回无穷大，并非所有错误都会返回零。把出错返回值当成有效值，会把一个超限输入意外变成最大允许值。

练习：分别解析 "255"、"256"、"-1"、" 12"，使用 ParseUint(s,10,8)，只有第一项应成功；空白不会自动修剪。如果业务允许空白，要显式 TrimSpace，并把规则写进测试。AppendInt 可以复用预分配缓冲区，但容量不够仍会分配；是否更快应通过实际基准确认。Quote 输出 Go 字符串字面量，不能替代 SQL 参数、HTML 转义或 JSON 编码。

## 🔗 相关条目

- 📄 **[errors 标准库](./09-errors.md)** - NumError 的 errors.As/Is 判别
- 📄 **[slices/maps 标准库](./13-slices-maps.md)** - 字符串切片处理组合
- 📄 **[encoding/json 包](./04-encoding-json.md)** - 结构化场景优先 JSON 而非手工转换
- 📄 **[flag 包](./16-flag.md)** - flag 内部即用 strconv 解析
- 🌐 **[pkg.go.dev/strconv](https://pkg.go.dev/strconv)** - 官方文档

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
