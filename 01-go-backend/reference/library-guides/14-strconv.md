# strconv - 字符串与基本类型互转

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

strconv 负责**字符串与基本类型（整型/浮点/布尔）之间的高性能转换**。与 `fmt.Sprintf` 的关系：strconv 专用且更快（无反射、无接口装箱）；序列化热路径（拼 SQL、写 CSV、生成日志字段）首选 Append 系列。

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

// Append：追加到已有 []byte，零分配热路径
buf = strconv.AppendInt(buf, 42, 10)
buf = strconv.AppendQuote(buf, s)     // 带 Go 字面量引号转义

// 引号处理
strconv.Quote("he\"llo")              // "\"he\\\"llo\""：加引号+转义
strconv.Unquote(`"hello"`)            // 去 Go 字面量引号
```

**ParseFloat 格式符**：`'f'`（无指数，如 3.14）、`'e'/'E'`（科学计数）、`'g'`（自动选择，与 `%g` 一致）、精度 -1 表示"最短能还原的表示"。

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

	// 4. Append 零分配拼接
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
- ✅ **正确做法**：解析族（Atoi/Parse*）失败返回零值 + `*NumError`，必须处理 err；这是外部输入（env/flag/HTTP 参数）的必经校验点。
- ❌ **错误做法**：用 `fmt.Sprintf("%d", x)` 拼接热路径。
- ✅ **正确做法**：`strconv.Itoa/AppendInt` 更快（无反射开销）；fmt 留给复合格式化。
- ❌ **错误做法**：`Atoi` 期望解析 int64 超范围值成功。
- ✅ **正确做法**：Atoi 等价 ParseInt(s, 10, 0)（平台位宽）；大数/指定位宽用 `ParseInt(s, base, 64)` 并检查 `ErrRange`。
- ❌ **错误做法**：ParseInt 进制参数传 0 想当然。
- ✅ **正确做法**：base=0 是"按前缀识别"（0x/0b/0o/0 前缀，下划线分隔符合法），base 显式 10 时纯数字——两者行为不同，选对语义。
- ❌ **错误做法**：Unquote 直接解用户原始 JSON 字符串。
- ✅ **正确做法**：Unquote 只认 **Go 字面量**规则；JSON 字符串交给 encoding/json。
- ❌ **错误做法**：Append 系列忘记接收返回值（`strconv.AppendInt(buf, ...)` 孤立调用）。
- ✅ **正确做法**：`buf = strconv.AppendInt(buf, ...)`——append 语义，可能扩容换底层数组。

## 🔗 相关条目

- 📄 **[errors 标准库](./09-errors.md)** - NumError 的 errors.As/Is 判别
- 📄 **[slices/maps 标准库](./13-slices-maps.md)** - 字符串切片处理组合
- 📄 **[encoding/json 包](./04-encoding-json.md)** - 结构化场景优先 JSON 而非手工转换
- 📄 **[flag 包](./16-flag.md)** - flag 内部即用 strconv 解析
- 🌐 **[pkg.go.dev/strconv](https://pkg.go.dev/strconv)** - 官方文档

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
