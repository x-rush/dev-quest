# 切片（Slice）语义

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

切片是 Go 对连续内存序列的**视图封装**：一个指向底层数组的指针 + 长度（len）+ 容量（cap）三元组。理解"切片是数组窗口而非数组本身"是掌握 Go 值语义、append 行为与内存泄漏问题的钥匙。

## 📖 语法 / 签名

```go
// 切片头（概念模型；实际运行时布局和大小不是语言契约）：ptr + len + cap
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
| `copy(dst, src)` | 拷贝 min(len(dst), len(src)) 个元素 | 取决于 dst/src 的存储；不自动分配，嵌套引用仍可能共享 |
| `append(s, v)` | 可能复用原数组（cap 足够），否则新分配 | 看情况 |

**append 的规范保证与实现细节**：容量足够时可复用原数组，不足时会分配足够大的新数组。具体增长比例、初次容量和内存规格取整不是语言契约，会随实现和元素大小变化。原先列出的固定容量序列不能作为跨版本验收标准；实验应记录本机结果，并验证数据和共享关系。

## 💡 示例

<!-- ninth-reference-case: {"id":"go-slice-full-expression","stdout":"[9 2 3]\n[9 8]\n"} -->
```go
package main

import "fmt"

func main() {
	a := []int{1, 2, 3}
	s := a[:1:1]
	s[0] = 9
	fmt.Println(a)
	s = append(s, 8)
	fmt.Println(s)
}
```

这个完整程序同时证明两件容易混淆的事：三索引切片不会隔离既有元素的写入，但会使随后超出容量的 `append` 分配新底层数组。

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
- ✅ **正确做法**：需要释放大数组引用时，使用 `clone := append([]T(nil), big[:1]...)` 或 slices.Clone 复制需要的元素；三索引切片仅限制 cap，不能解除原数组引用。
- ❌ **错误做法**：循环里往多个结果切片 append 同一来源切片，事后修改互相串数据。
- ✅ **正确做法**：明确每次 append 的容量来源；需要独立数据就先复制。
- ❌ **错误做法**：用 `s == nil` 判断切片是否为空。
- ✅ **正确做法**：判空用 `len(s) == 0`（nil 切片和空切片都覆盖）。
- ❌ **错误做法**：多 goroutine 并发 append 同一切片。
- ✅ **正确做法**：append 非并发安全，用互斥锁保护或每 goroutine 独立切片后合并。

<!-- full-library-explanation -->
## 容量隔离、元素复制和释放内存是三件事

前置是数组、指针和 append。完整切片表达式限制后续 append 可复用的容量，但没有复制已有元素，也没有断开对原底层数组的引用。小窗口长期持有大数组时，仅把 cap 改小不能让原数组被回收。

练习用 `a := []int{1, 2, 3}` 和 `s := a[:1:1]`：执行 `s[0] = 9` 后 a 应变成 `[9 2 3]`；执行 `s = append(s, 8)` 后，s 为 `[9 8]`，a 不再因这次 append 改变。再用 make 加 copy 得到独立存储，区分“限制扩展”与“复制数据”。

copy 复制元素值，若元素本身含切片、指针或 map，内部引用仍可能共享。性能实验记录 len/cap 的变化即可，不把某个编译器上的容量序列当成语言契约；需要独立生命周期时，先明确复制到哪一层。

## 🔗 相关条目

- 📄 **[map 语义](./11-map-semantics.md)** - 同为引用语义类型，nil 行为对比
- 📄 **[nil 语义汇总](./15-nil-semantics.md)** - nil 切片 vs 空切片
- 📄 **[Go 数据类型详解](./04-go-data-types.md)** - 数组与切片的类型区别
- 📄 **[slices/maps 标准库](../library-guides/13-slices-maps.md)** - 泛型切片工具函数
- 🌐 **[Go Slices: usage and internals](https://go.dev/blog/slices-intro)** - 官方权威讲解
- 🌐 **[pkg.go.dev/builtin#append](https://pkg.go.dev/builtin#append)** - append 规范语义

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
