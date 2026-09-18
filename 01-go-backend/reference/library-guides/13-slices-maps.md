# slices / maps - 泛型集合工具

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

`slices` 与 `maps` 是 Go 1.21+ 的**泛型集合工具包**：把过去每个项目都手写的循环（查找、去重、排序、克隆、键值收集）变成带编译期类型检查的标准库调用。心智模型——切片是"有序序列"用 slices；map 是"键值集合"用 maps；各函数的修改和分配行为不同，必须分别查看约定；返回切片的变形操作通常要接收返回值。

## 📖 语法 / 签名

```go
package main

import (
	"cmp"
	"fmt"
	"maps"
	"slices"
	"strings"
)

func main() {
	values := []int{5, 2, 8, 2, 9}
	fmt.Println(slices.Contains(values, 8), slices.Index(values, 2)) // comparable 查找
	fmt.Println(slices.Equal(values, []int{5, 2, 8, 2, 9}))
	fmt.Println(slices.EqualFunc([]string{"Go"}, []string{"go"}, strings.EqualFold))
	fmt.Println(slices.Compare([]int{1, 2}, []int{1, 3})) // 字典序：-1/0/1

	slices.Sort(values) // 升序（需 Ordered）
	slices.SortFunc(values, func(a, b int) int { return cmp.Compare(b, a) })
	fmt.Println(values, slices.IsSorted(values))
	slices.Sort(values)
	index, found := slices.BinarySearch(values, 8) // BinarySearch 前必须已排序
	fmt.Println(index, found)

	copyOfValues := slices.Clone(values) // 浅拷贝，新底层数组
	copyOfValues = slices.Insert(copyOfValues, 0, 100)
	copyOfValues = slices.Delete(copyOfValues, 0, 1) // 删 [i,j)，移动尾部元素
	copyOfValues = slices.DeleteFunc(copyOfValues, func(value int) bool { return value%2 == 0 })
	copyOfValues = slices.Grow(copyOfValues, 4)
	compacted := slices.Compact([]int{1, 1, 2, 2, 3})
	slices.Reverse(compacted) // 原地反转
	fmt.Println(copyOfValues, compacted, slices.Max(values), slices.Min(values)) // 空切片 Max/Min 会 panic

	first := map[string]int{"a": 1, "b": 2}
	second := maps.Clone(first) // 浅拷贝
	maps.Copy(second, map[string]int{"b": 20, "c": 3})
	fmt.Println(maps.Equal(first, second))
	maps.DeleteFunc(second, func(key string, value int) bool { return value > 2 })
	for key := range maps.Keys(second) { // Go 1.23+：Keys 返回 iter.Seq
		fmt.Println(key)
	}
	for value := range maps.Values(second) {
		fmt.Println(value)
	}
}
```

**迭代器要点（Go 1.23+）**：标准库在 Go 1.23 新增的 `maps.Keys/Values` 返回迭代器而非切片，而是 `iter.Seq`（可 `for k := range maps.Keys(m)` 直接遍历）；需要切片时用 `slices.Collect(maps.Keys(m))`。

## 💡 示例

```go
package main

import (
	"fmt"
	"maps"
	"slices"
)

func main() {
	s := []int{5, 2, 8, 2, 9}

	// 1. 查找与比较
	fmt.Println(slices.Contains(s, 8)) // true
	fmt.Println(slices.Index(s, 2))    // 1

	// 2. 排序与搜索
	slices.Sort(s)                     // [2 2 5 8 9]
	fmt.Println(s)
	i, ok := slices.BinarySearch(s, 8) // 已排序才能二分
	fmt.Println(i, ok)                 // 3 true

	// 3. 克隆与增删（注意：Delete 修改底层数据，Insert 可能扩容；都要接收新切片头）
	c := slices.Clone(s)
	c = slices.Insert(c, 0, 100) // 头部插入
	fmt.Println(c)               // [100 2 2 5 8 9]
	c = slices.Delete(c, 0, 2)   // 删 [0,2)
	fmt.Println(c, len(s))       // [2 5 8 9] 5（s 不受影响，Clone 功劳）
	c = slices.DeleteFunc(c, func(v int) bool { return v%2 == 0 })
	fmt.Println(c)               // [5 9]

	// 4. 极值
	fmt.Println(slices.Max(s), slices.Min(s)) // 9 2

	// 5. maps：迭代器收集与克隆
	m := map[string]int{"b": 2, "a": 1, "c": 3}
	keys := slices.Sorted(maps.Keys(m)) // Sorted 收集+排序一步到位
	fmt.Println(keys)                   // [a b c]

	m2 := maps.Clone(m)
	m2["d"] = 4
	fmt.Println(maps.Equal(m, m2)) // false

	maps.DeleteFunc(m2, func(k string, v int) bool { return v > 2 })
	fmt.Println(slices.Sorted(maps.Keys(m2))) // [a b]
}
```

**与手写循环对比**：`slices.Contains(s, v)` 等价于 `for _, e := range s { if e == v { return true } }`——标准库版本的收益是**意图直读**（一眼看出"在找元素"）与类型安全（`Contains([]int, "x")` 编译报错，正确编写的具体类型循环同样受类型检查，标准库减少了重复实现）。

## ⚠️ 常见陷阱

- ❌ **错误做法**：以为 `slices.Delete` 返回新切片、原切片未动。
- ✅ **正确做法**：Delete/Compact 修改底层数据并返回新切片头，Insert 可能复用或更换数组，Reverse 就地修改且没有返回值。Delete/Insert/Compact 要接收结果；需要隔离外层数据时先 Clone。
- ❌ **错误做法**：`BinarySearch` 前忘了排序。
- ✅ **正确做法**：二分要求升序（与 Sort 一致）；无序用 `slices.Index` 线性查。
- ❌ **错误做法**：对空切片调 `slices.Max/Min`。
- ✅ **正确做法**：空切片 panic；先判 `len(s) > 0` 再用。
- ❌ **错误做法**：`keys := maps.Keys(m)` 当切片用。
- ✅ **正确做法**：1.23+ 返回 `iter.Seq`——直接 range 遍历，或 `slices.Collect/slices.Sorted` 物化成切片。
- ❌ **错误做法**：`maps.Clone` 后以为深拷贝。
- ✅ **正确做法**：Clone 只拷一层；value 含 slice/map/指针时仍共享内层数据。
- ❌ **错误做法**：SortFunc 比较器里返回 `a - b`（溢出风险）。
- ✅ **正确做法**：用 `cmp.Compare(a, b)` 构造比较结果。

<!-- full-library-explanation -->
## 返回的新长度与共享的底层数据

前置是切片的长度、容量与底层数组。slices.Delete 返回更新后的切片头，原变量的长度不会自动改变；它会移动底层元素并清理尾部引用，因此旧切片头虽然仍可使用，却已不再表示原来的数据。Insert 可能扩容到新数组，也可能复用旧数组，不能把是否隔离建立在当前一次运行的容量上。Reverse 就地修改且没有返回值，与 Delete 的调用形式不同。

Clone 适合隔离外层元素排列。例如 []int 的 Clone 后排序不会改原切片；但 [][]int 的 Clone 仍共享每一个内层 []int。对于 map[string][]int 也是同样道理，maps.Clone 只建立新 map，不递归复制值。是否需要深复制由数据所有权决定，不能靠函数名猜测。

练习：令 s 为 []int{1,2,3}，先执行 result := slices.Delete(s,0,1)，预测 len(result) 为 2，而 len(s) 仍为 3；不要继续把 s 当作未修改的原始数据。第二题将 map 的键排序后再输出，两次运行应得到相同的键顺序；直接 range map 没有这种保证。大数据中还要区分 Contains 的线性扫描与排序后 BinarySearch 的搜索成本，排序本身并非免费。

## 🔗 相关条目

- 📄 **[切片语义](../language-concepts/10-slice-semantics.md)** - Delete 原地修改的底层原因
- 📄 **[map 语义](../language-concepts/11-map-semantics.md)** - map 遍历顺序随机与排序收集
- 📄 **[Go 泛型](../language-concepts/09-generics.md)** - 泛型约束 Ordered/comparable 的基础
- 📄 **[strconv 包](./14-strconv.md)** - 字符串切片排序的常见搭档
- 🌐 **[pkg.go.dev/slices](https://pkg.go.dev/slices)** - 官方文档
- 🌐 **[pkg.go.dev/maps](https://pkg.go.dev/maps)** - 官方文档

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
