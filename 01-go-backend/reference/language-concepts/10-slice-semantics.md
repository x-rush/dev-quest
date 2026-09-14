# 切片（Slice）语义

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

切片是 Go 对连续内存序列的**视图封装**：一个指向底层数组的指针 + 长度（len）+ 容量（cap）三元组。理解"切片是数组窗口而非数组本身"是掌握 Go 值语义、append 行为与内存泄漏问题的钥匙。

## 📖 语法 / 签名

```go
// 切片头（runtime 内部表示，约 24 字节）：ptr + len + cap
type slice struct {
    array unsafe.Pointer // 指向底层数组某元素
    len   int            // 当前元素个数
    cap   int            // 从 ptr 起底层数组可用长度
}

// 创建方式
s1 := []int{1, 2, 3}          // 字面量：分配独立底层数组
s2 := make([]int, 3, 10)      // make：len=3，cap=10，元素为零值
var s3 []int                  // nil 切片：len=cap=0，ptr=nil
s4 := arr[1:3]                // 从数组/切片切出：共享原底层数组

// 完整切片表达式 s[low:high:max]：限制 cap，隔离写回
s5 := arr[1:3:3]              // cap = max - low，append 不再写回原数组
```

| 操作 | 结果 | 是否共享底层数组 |
|------|------|------------------|
| `make([]T, n)` | 新分配，元素为零值 | 否（独立数组） |
| `s[a:b]` | 新切片头，`len=b-a`，`cap=cap(s)-a` | **是** |
| `s[a:b:c]` | 新切片头，`cap=c-a` | 是（但 append 越界会另分配） |
| `copy(dst, src)` | 拷贝 `min(len(dst), len(src))` 个元素 | 否（元素级复制） |
| `append(s, v)` | 可能复用原数组（cap 足够），否则新分配 | 看情况 |

**append 扩容规则（Go 1.18+，runtime.growslice）**：
- 期望容量 ≤ 256：新容量直接翻倍。
- 期望容量 > 256：按约 1.25 倍逐步增长（含平滑过渡公式），且最终容量经过内存分配器规格取整，实际值可能明显大于公式值；小元素首次 append 也常因规格取整一次到位。

```go
// go1.25 实测（linux/amd64，[]int）：
s := make([]int, 0)
s = append(s, 1)  // cap 4（首次即按分配器规格取整，非 1）
// 翻倍段：4 → 8 → 16 → 32 → 64 → 128 → 256 → 512
// 平滑段：512 → 848 → 1280 → 1792 → 2560 → 3408 → 5120（约 1.25×+取整）
// 具体数值随元素大小与平台对齐而变，勿硬编码依赖
```

## 💡 示例

```go
package main

import "fmt"

func main() {
	// 1. 底层数组共享：改切片会"穿透"到原数组
	arr := [5]int{1, 2, 3, 4, 5}
	s := arr[1:3]        // len=2, cap=4（从 arr[1] 起还有 4 个位置）
	s[0] = 99            // 写穿透：arr 变为 [1 99 3 4 5]
	fmt.Println(arr, s)  // [1 99 3 4 5] [99 3]

	// 2. append 写回：cap 足够时原地写，污染原数组
	sub := arr[1:3]      // cap=4，还有空位
	sub = append(sub, 0) // 覆盖了 arr[3]！
	fmt.Println(arr)     // [1 99 3 0 5]

	// 3. 切片头拷贝：b 复制的是 ptr/len/cap，数据仍共享
	b := s               // 与 s 同底层数组
	b = append(b, 7)     // cap 仍足够 → 依然写回原数组
	fmt.Println(arr, &s[0] == &b[0]) // [1 99 3 7 5] true

	// 4. 完整切片表达式：cap 截断，append 必然另分配
	big := arr[1:3:3]    // len=2, cap=2
	big = append(big, 8) // 超出 cap → 新数组，arr 不受影响
	fmt.Println(arr)     // [1 99 3 7 5]（未变）

	// 5. copy 与元素复制：与底层数组彻底脱钩
	dst := make([]int, 2)
	n := copy(dst, s)    // n = min(len(dst), len(s)) = 2
	fmt.Println(dst, n)  // [99 3] 2
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：函数内 `append(s, x)` 后假设调用方看到的 `s` 变长了。
- ✅ **正确做法**：append 可能返回新切片头，必须接收返回值并回传：`s = append(s, x)`；对外暴露"会增长"的数据用指针 `*[]T` 或返回新切片。
- ❌ **错误做法**：大切片上 `big[:1]` 截取小片段长期持有——底层数组整体被引用，无法 GC。
- ✅ **正确做法**：截取时用三索引 `big[:1:1]` 隔离 cap，或 `clone := append([]T(nil), big[:1]...)` / `slices.Clone` 复制需要的部分。
- ❌ **错误做法**：循环里往多个结果切片 append 同一来源切片，事后修改互相串数据。
- ✅ **正确做法**：明确每次 append 的容量来源；需要独立数据就先复制。
- ❌ **错误做法**：用 `s == nil` 判断切片是否为空。
- ✅ **正确做法**：判空用 `len(s) == 0`（nil 切片和空切片都覆盖）。
- ❌ **错误做法**：多 goroutine 并发 append 同一切片。
- ✅ **正确做法**：append 非并发安全，用互斥锁保护或每 goroutine 独立切片后合并。

## 🔗 相关条目

- 📄 **[map 语义](./11-map-semantics.md)** - 同为引用语义类型，nil 行为对比
- 📄 **[nil 语义汇总](./15-nil-semantics.md)** - nil 切片 vs 空切片
- 📄 **[Go 数据类型详解](./04-go-data-types.md)** - 数组与切片的类型区别
- 📄 **[slices/maps 标准库](../library-guides/13-slices-maps.md)** - 泛型切片工具函数
- 🌐 **[Go Slices: usage and internals](https://go.dev/blog/slices-intro)** - 官方权威讲解
- 🌐 **[pkg.go.dev/builtin#append](https://pkg.go.dev/builtin#append)** - append 规范语义

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
