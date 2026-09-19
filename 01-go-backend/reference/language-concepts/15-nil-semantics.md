# nil 语义汇总

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

nil 是 6 类值（pointer/slice/map/channel/func/interface）的**零值**，但每种类型对 nil 的容忍度完全不同：有的只读安全、有的彻底不可用、有的还能合法增删。`error` 不是第七类；它是接口类型的常见用法，因此沿用 interface 的 nil 规则。本条目是各类型 nil 行为的**单一汇总表**，判断姿势一次讲清。

## 📖 语法 / 签名：各类型 nil 行为总表

| 类型 | `== nil` 判断 | 读操作 | 写操作 | 关键陷阱 |
|------|---------------|--------|--------|----------|
| `pointer` | 直接 `p == nil` | 解引用 panic | 解引用 panic | 解引用 nil 是最常见 panic |
| `slice` | `s == nil` 合法但 `len(s)==0` 更通用 | `len/cap/range/append` 全安全 | `append` **合法**（自动分配） | `s[i]` 索引越界 panic；与空切片 `[]T{}` JSON 序列化不同 |
| `map` | 合法 | 读/`len`/`delete`/`range` 安全 | **写入 panic** | nil map 可读的假象让人以为可用 |
| `channel` | 合法 | 接收**永久阻塞** | 发送**永久阻塞** | `close(nil)` panic；select 中 nil 分支被忽略（可作屏蔽器） |
| `func` | 合法 | 不可读 | 调用 panic | 回调可选时先判 nil 再调用 |
| `interface` | 仅当**类型+值都 nil** 才为 true | 调方法 panic | 不适用 | 装入 nil 指针后 `i != nil`（见接口条目） |
| `error` | 同 interface 规则 | 调 `Error()` panic | 不适用 | 具体指针 nil 装包后 `err != nil` |

```go
// 判断姿势速查
if s == nil {}        // 切片：合法，但通常想要的是——
if len(s) == 0 {}     // 切片判空：nil 与空都覆盖（推荐）
if m == nil {}        // map：写入前检查，或保证 make 过
if f != nil { f() }   // func：调用前检查
if err != nil {}      // error：标准三段式
// channel/pointer：判断合法，重点是理解"不 panic 但阻塞/崩溃"的行为
```

## 💡 示例

<!-- go-rust-node-tenth-case: go-nil-semantics -->
<!-- doc-verify:go-nil-value-boundaries -->
```go
package main

import "fmt"

func main() {
	// 1. nil slice：append 合法，len/range 安全（Go 惯用的"零值可用"）
	var s []int
	fmt.Println(len(s), cap(s)) // 0 0
	for range s {}              // 安全
	s = append(s, 1)            // 合法：自动分配底层数组
	fmt.Println(s)              // [1]

	// 2. nil map：读安全、写 panic（对照记忆）
	var m map[string]int
	fmt.Println(m["k"]) // 0（读返回零值，不 panic）
	fmt.Println(len(m)) // 0
	// m["k"] = 1        // panic: assignment to entry in nil map
	m = make(map[string]int) // 写之前必须 make
	m["k"] = 1

	// 3. nil func：调用 panic，回调先判空
	var cb func()
	fmt.Println(cb == nil) // true
	if cb != nil {
		cb()
	}

	// 4. nil interface：只有"零值接口"才等于 nil
	var i interface{ Speak() }
	fmt.Println(i == nil) // true（类型与值都是 nil）

	// 5. nil pointer：解引用 panic；方法有 nil 接收者防御则可调用
	type Node struct{ v int }
	var p *Node
	fmt.Println(p == nil) // true
	// _ = p.v            // panic: invalid memory address or nil pointer dereference
}
```

**"零值可用"设计哲学**：nil slice（append/range/len 安全）与 zero-value mutex、bytes.Buffer 一样，让 `var x T` 直接可用是 Go 的惯用风格；而 map/channel 因实现需要显式初始化，破坏了这一致性——写代码时对这两类要格外记得 make。

## ⚠️ 常见陷阱

- ❌ **错误做法**：`var m map[string]int` 直接写入，或结构体内嵌 map 字段不初始化。
- ✅ **正确做法**：构造函数里 make，或声明即初始化 `m := map[string]int{}`。
- ❌ **错误做法**：把"nil slice append 合法"推广到"零值 map 也能写"。
- ✅ **正确做法**：记住分界——slice/map 二者零值行为**不对称**：nil slice 可 append，nil map 不可写。
- ❌ **错误做法**：`if err != nil` 之前对 err 做了 `err.Error()` 之类的假设。
- ✅ **正确做法**：error 是接口，先判 nil 再用；警惕"nil 指针装进 error"（见接口条目的 mightFail 例子）。
- ❌ **错误做法**：向 nil channel 发送数据并期待"报错提示"。
- ✅ **正确做法**：nil channel 不报错而是**永久阻塞**（timeout 场景的隐形泄漏源）；初始化后再用，select 中可利用其"永不就绪"屏蔽分支。
- ❌ **错误做法**：JSON 序列化时混用 `var s []T` 与 `s := []T{}`，导致 `null` 与 `[]` 输出不一致。
- ✅ **正确做法**：对外 API 返回统一形态——要么都 `make([]T, 0)`，要么接收端兼容 null（见 encoding/json 条目）。

<!-- full-library-explanation -->
## nil 是具体类型的零值状态

前置是接口、指针和容器。nil 不是“任何操作都失败”的统一对象：nil slice 可以 append，nil map 可以读取但不能写入，nil channel 收发会等待。先确认静态类型，再查相应操作，比先加一层 nil 判断更可靠。

练习分别声明 nil slice、空 slice、nil map 和空 map，记录 len、与 nil 的比较以及 JSON 输出。使用 encoding/json 默认行为时，nil slice 输出 null，非 nil 空 slice 输出 []；接口协议需要固定形状时，在输出边界明确构造。

error 自身就是接口，不是第七种独立 nil 类型。装有 nil 指针的接口仍可调用指针接收者方法，是否 panic 取决于方法实现；零值接口则没有可调用的动态方法。把“调用方法”与“解引用字段”分开判断。

## 🔗 相关条目

- 📄 **[切片语义](./10-slice-semantics.md)** - nil slice 与空 slice 的底层差异
- 📄 **[map 语义](./11-map-semantics.md)** - nil map 行为详解
- 📄 **[channel 语义](./12-channel-semantics.md)** - nil channel 阻塞规则表
- 📄 **[接口语义](./13-interface-semantics.md)** - "nil 接口 vs 装 nil 的接口"
- 📄 **[defer/panic/recover](./14-defer-panic-recover.md)** - nil 解引用 panic 与 recover 边界
- 🌐 **[Go spec: nil slices/maps/channels](https://go.dev/ref/spec#Slice_types)** - 语言规范

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
