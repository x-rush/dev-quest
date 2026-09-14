# map 语义

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

map 是 Go 内置的**哈希表**：key 必须可比较类型，value 任意类型。map 是引用语义——赋值与传参共享同一份底层数据；同时它是少数"零值不可用"的内置类型之一。

## 📖 语法 / 签名

```go
// 创建
var m1 map[string]int          // nil map：可读不可写
m2 := make(map[string]int)     // 空且可用
m3 := make(map[string]int, 100) // 预估容量 100，减少扩容
m4 := map[string]int{"a": 1, "b": 2} // 字面量

// 读写与删除
v := m["k"]        // key 不存在返回 value 零值（无报错）
v, ok := m["k"]    // 双值形式区分"零值"与"不存在"
m["k"] = v         // 写入（nil map 会 panic）
delete(m, "k")     // 删除不存在的 key 是安全 no-op
```

| 特性 | 语义 |
|------|------|
| key 类型 | 必须 `comparable`（可 `==`）；不可用 slice/map/func |
| 零值 | `nil`，读安全（返回零值）、写 panic、delete 安全、len 为 0 |
| 遍历顺序 | **故意随机化**，每次运行可能不同 |
| 元素取址 | map 元素**不可寻址**（`&m["k"]` 编译错误） |
| value 类型 | 可以是 func/channel/slice/interface 等零值即 nil 的类型 |
| 并发 | 无内置同步，并发读写会直接 fatal（不可 recover） |
| 比较 | map 不可比较（除与 nil 比较） |

**迭代顺序随机化的设计意图**：强制开发者不依赖哈希表内部实现顺序。即使"恰好"某次运行有序，也不能作为依赖。需要有序输出时先收集 key 排序。

## 💡 示例

```go
package main

import (
	"fmt"
	"sort"
	"sync"
)

func main() {
	// 1. 双值读取 + 安全删除
	counts := map[string]int{"go": 3}
	if n, ok := counts["rust"]; ok {
		fmt.Println(n)
	} else {
		fmt.Println("no rust") // 不存在不报错，靠 ok 区分
	}
	delete(counts, "rust") // 删除不存在的 key：no-op，不 panic
	delete(counts, "go")

	// 2. 有序遍历：先排 key
	ages := map[string]int{"carol": 30, "alice": 25, "bob": 28}
	keys := make([]string, 0, len(ages))
	for k := range ages {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		fmt.Println(k, ages[k]) // 每次输出顺序一致：alice bob carol
	}

	// 3. 并发安全：RWMutex 包装 vs sync.Map
	var mu sync.RWMutex
	safeMap := make(map[string]int)
	mu.Lock()
	safeMap["hits"] = 1
	mu.Unlock()

	var sm sync.Map
	sm.Store("hits", 1)
	if v, ok := sm.Load("hits"); ok {
		fmt.Println(v.(int)) // 需要类型断言，无编译期类型安全
	}
}
```

**互斥锁 map vs sync.Map 怎么选**：读多写少、key 集合基本稳定（如配置缓存）→ `sync.Map`；读写均衡、需要类型安全、可用 `slices`/`maps` 工具函数 → `RWMutex` + 普通 map。大多数业务代码首选后者，语义更直白。

## ⚠️ 常见陷阱

- ❌ **错误做法**：`var m map[string]int` 后直接 `m["k"] = 1`。
- ✅ **正确做法**：nil map 写入 panic（`assignment to entry in nil map`）；先 `make` 再写。
- ❌ **错误做法**：依赖 map 遍历顺序输出结果。
- ✅ **正确做法**：收集 key 到切片，排序后遍历。
- ❌ **错误做法**：`&m["k"]` 或对结构体 value 的字段直接赋值 `m["k"].field = x`（value 为结构体时）。
- ✅ **正确做法**：map 元素不可寻址；先读出整体、修改后写回，或让 value 是指针 `map[string]*T`。
- ❌ **错误做法**：多 goroutine 直接读写同一 map，期望靠 recover 兜底。
- ✅ **正确做法**：并发读写触发的是 `fatal error: concurrent map writes`，**不可被 recover**，进程直接崩溃；必须用锁或 sync.Map。
- ❌ **错误做法**：以为 nil map 一切操作都 panic。
- ✅ **正确做法**：nil map 读/len/delete 都安全；只有"写"危险。初始化纪律：结构体里的 map 字段在构造函数中 make。
- ❌ **错误做法**：把浮点数 `NaN` 当 key。
- ✅ **正确做法**：`NaN != NaN`，写入后永远查不到自身；避免用 NaN 作 key。

## 🔗 相关条目

- 📄 **[切片语义](./10-slice-semantics.md)** - 引用语义与 nil 行为对比
- 📄 **[nil 语义汇总](./15-nil-semantics.md)** - nil map 写入 panic 汇总表
- 📄 **[Go 并发基础](./08-concurrency-basics.md)** - 并发安全的内存模型背景
- 📄 **[slices/maps 标准库](../library-guides/13-slices-maps.md)** - maps.Keys/Values/Clone 工具
- 📄 **[sync 包](../library-guides/06-sync.md)** - RWMutex/sync.Map 详解
- 🌐 **[pkg.go.dev/builtin#map](https://pkg.go.dev/builtin#map)** - 内置 map 规范

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
