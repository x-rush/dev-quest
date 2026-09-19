# 复合数据类型：数组、切片、映射与结构体

## 先理解，再动手

数组把长度放进类型，切片描述底层数组的一段，map 根据键找值，struct 给一组不同类型的数据命名。先按用途选，不按语法长短选。

**本节自测**：令 a 为 []int{1,2}，b := a，再修改 b[0]。随后用复制得到独立切片再修改。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

第一次 a 也变化，因为共享底层数组；独立复制后修改不再影响 a。append 可能重新分配，不能据此假定始终共享。

</details>

> **文档简介**: 掌握Go四种核心复合类型——数组、切片、映射和结构体，理解它们各自的内存语义与适用场景

> **目标读者**: 已掌握变量与基础数据类型、准备处理集合数据的Go初学者

> **前置知识**: 已完成 [变量、常量和基础数据类型](03-variables-constants.md)，理解零值与类型推断

> **预计时长**: 2-3小时学习 + 练习

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `basics/programming-fundamentals` |
| **难度** | ⭐ (1/5) |
| **标签** | `#数组` `#切片` `#映射` `#结构体` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **验证范围** | 文末 4 个完整实验；其他片段用于逐步讲解 |

</details>

## 🎯 学习目标

通过本文档学习，您将能够：
- 声明和初始化数组、切片、映射、结构体
- 理解"数组是值类型、切片共享底层数组"的核心语义
- 安全地使用 `append`、`copy`、`delete` 等内建操作
- 用 comma-ok 惯用法判断映射键是否存在
- 组合使用结构体与切片，编写小型数据模型

## 📝 数组：固定长度的值类型

### 1. 声明与初始化

数组长度是类型的一部分，`[3]int` 和 `[5]int` 是不同类型：

```go
var arr [3]int          // 零值数组: [0 0 0]
arr[0] = 1
nums := [3]int{1, 2, 3}

// 用 ... 让编译器数元素个数
primes := [...]int{2, 3, 5, 7, 11}
fmt.Println(len(primes)) // 5
```

### 2. 数组是值类型

**赋值和传参会复制整个数组**——这是Go与C数组最关键的区别：

```go
nums := [3]int{1, 2, 3}
b := nums
b[0] = 100
fmt.Println(nums, b) // [1 2 3] [100 2 3] —— nums 未被修改
```

### 3. 遍历

> 💡 这里用到了 for/range 循环，语法详见 [06-control-structures.md](06-control-structures.md)。

```go
for i, v := range primes {
    fmt.Println(i, v) // 索引 + 值
}
```

> 💡 实际开发中数组很少直接使用，绝大多数场景用**切片**。数组的价值在于：固定长度语义（如 IPv4 地址 `[4]byte`）以及作为切片的底层存储。

## 📝 切片：动态数组

### 1. 创建方式

```go
// make 创建: 长度 3, 容量 5
s := make([]int, 3, 5)
fmt.Println(len(s), cap(s)) // 3 5

// 字面量创建（最常用）
langs := []string{"Go", "Python", "Java"}
```

### 2. append 与自动扩容

```go
s := make([]int, 3, 5)
s = append(s, 10, 11) // len: 3→5, 恰好用满容量
fmt.Println(s, len(s), cap(s)) // [0 0 0 10 11] 5 5

// 超过容量时分配更大的底层数组，地址改变
big := make([]int, 0, 2)
for i := 0; i < 100; i++ {
    big = append(big, i)
}
fmt.Println(cap(big)) // 已扩容，不再是 2
```

### 3. 切片表达式与共享底层数组陷阱

切片表达式 `[开始:结束)` 含头不含尾：

```go
langs := []string{"Go", "Python", "Java"}
sub := langs[1:3]
fmt.Println(sub) // [Python Java]
```

**切片不复制数据，只是底层数组的一个视图**。修改子切片会影响原切片：

```go
sub[0] = "Rust"
fmt.Println(langs) // [Go Rust Java] —— 原切片被改了！
```

### 4. copy：真正复制数据

```go
dst := make([]string, len(langs))
n := copy(dst, langs)
fmt.Println(n, dst) // 3 [Go Rust Java] —— 这里复制的是 string 元素
```

`copy` 复制 `min(len(dst), len(src))` 项，允许源和目标重叠。仅预留容量、长度为 0 的目标复制不了元素。复制 `[][]int` 或 `[]*T` 时只复制内部切片值或指针，仍共享内部对象。

> ⚠️ **必须掌握的陷阱**：无论是否扩容，另一个切片变量执行 append 都不会自动改变调用方原切片的长度；未扩容时可能覆盖共享数组中原长度以外的数据。函数追加后应返回切片，调用方接收返回值。三下标 `s[:len(s):len(s)]` 限制容量，可让后续非空追加分配新数组，但直接修改已有元素仍会共享。

## 📝 映射：键值对集合

### 1. 创建与基本操作

```go
// make 创建 —— nil map 不能写入！
ages := make(map[string]int)
ages["alice"] = 30
ages["bob"] = 25

// 字面量创建
scores := map[string]int{"go": 100, "rust": 99}
```

### 2. 读取：键不存在返回零值

```go
fmt.Println(ages["alice"])       // 30
fmt.Println(ages["carol"])       // 0 —— 不存在的键返回 int 零值，不报错
```

### 3. comma-ok 惯用法

> 💡 这里用到了 `if` 条件判断，语法详见 [06-control-structures.md](06-control-structures.md)。

区分"值就是零值"和"键不存在"：

```go
if age, ok := ages["bob"]; ok {
    fmt.Println("bob 存在, 年龄:", age)
}
```

### 4. 删除与遍历

```go
delete(ages, "alice")
_, ok := ages["alice"]
fmt.Println(ok) // false

// 遍历顺序没有保证；需要有序输出时先对键排序
for name, age := range ages {
    fmt.Println(name, age)
}
```

> ⚠️ **nil map 陷阱**：`var m map[string]int` 声明的映射是 nil，**读取返回零值，但写入会 panic**。始终用 `make` 或字面量初始化。向 nil 切片 `append` 则是安全的。

> 💡 映射的值可以是任意类型，包括结构体——这是组织配置、索引数据的常见手法。

## 📝 结构体：自定义聚合类型

### 1. 定义与创建

```go
type Point struct {
    X, Y int
}

p1 := Point{X: 1, Y: 2}   // 字段名初始化（推荐）
p2 := Point{3, 4}          // 同类型字段调换顺序可能静默改变含义，优先具名初始化
var p3 Point               // 零值: {0 0}
```

### 2. 字段访问与指针

通过指针访问字段时**自动解引用**，无需写 `(*pp).Y`：

```go
p1 := Point{X: 1, Y: 2}
pp := &p1
pp.Y = 20 // 等价于 (*pp).Y = 20
fmt.Println(p1) // {1 20}
```

### 3. 结构体是值类型

与数组一样，赋值和传参复制结构体字段的值；其中的切片、map、指针仍可引用共享数据，外层复制不等于深拷贝：

```go
p4 := p1
p4.X = 999
fmt.Println(p1, p4) // {1 20} {999 20} —— p1 未受影响
```

需要修改原结构体或避免大结构体复制开销时，使用指针（这也是"方法接收者选值还是指针"的基础，见 [函数和方法](05-functions-methods.md)）。

### 4. 可比较性

字段全部可比较时，结构体可以用 `==` 直接比较：

```go
p2 := Point{3, 4}
fmt.Println(p2 == Point{X: 3, Y: 4}) // true
```

> ⚠️ 含切片、映射、函数字段的**结构体不可比较**，编译器会直接报错。若字段类型为接口，结构体在静态类型上可比较，但字段装入切片等不可比较动态值后参与比较仍可能 panic。`map[any]V` 使用切片动态值作键也会 panic。

## 📝 组合示例：结构体切片

结构体 + 切片是Go中最常见的数据建模组合（对应真实项目中的记录列表）：

```go
package main

import "fmt"

type Todo struct {
    Title string
    Done  bool
}

func main() {
    list := []Todo{
        {Title: "学习数组", Done: true},
        {Title: "学习切片"},
        {Title: "学习映射"},
    }
    list = append(list, Todo{Title: "学习结构体"})

    done := 0
    for _, t := range list {
        if t.Done {
            done++
        }
    }
    fmt.Printf("共 %d 项, 完成 %d 项\n", len(list), done)
    // 共 4 项, 完成 1 项
}
```

## ⚠️ 常见陷阱速查

| 陷阱 | 现象 | 正确做法 |
|------|------|----------|
| nil map 写入 | panic: assignment to entry in nil map | `make(map[K]V)` 或字面量初始化 |
| 子切片修改污染原切片 | 子切片赋值后原切片"莫名"变化 | 需要独立数据时用 `copy` |
| append 不把结果传回调用者 | 原切片长度未更新，底层元素可能已修改 | 返回新切片并接收返回值 |
| 依赖 map 遍历顺序 | 顺序没有保证，也可能重复 | 先排序键再遍历 |
| 只看字段数决定使用指针 | 可能引入共享修改与额外逃逸 | 先定义值语义，再测量成本 |

## 📈 性能提示

### 预分配切片容量

已知元素数量时用 `make([]T, 0, n)` 预分配，避免 append 反复扩容复制：

```go
ids := make([]int64, 0, len(users))
for _, u := range users {
    ids = append(ids, u.ID)
}
```

### 大结构体传指针

指针大小依平台而定，不能固定假设为 8 字节。按值传参在语言语义上复制字段；实际机器代码可能经过优化。指针会引入共享修改、逃逸与 GC 成本，不能仅凭字段多就断言更快；先确定是否需要修改原值，再用 benchmark 判断性能。

## 🔗 文档交叉引用

### 相关文档
- 📄 **[变量、常量和基础数据类型]**: [03-variables-constants.md](03-variables-constants.md) - 本文的前置知识
- 📄 **[函数和方法]**: [05-functions-methods.md](05-functions-methods.md) - 方法接收者的值/指针选择
- 📄 **[控制结构]**: [06-control-structures.md](06-control-structures.md) - for/range 遍历细节
- 📄 **[Go 标准库字典: slices 与 maps]**: [../reference/library-guides/01-go-standard-library.md](../reference/library-guides/01-go-standard-library.md) - slices/maps 泛型工具包

### 参考资源
- 📖 **[Go 语言规范: 复合类型]**: https://go.dev/ref/spec#Composite_types
- 📖 **[Go Slices: usage and internals]**: https://go.dev/blog/slices-intro
- 📖 **[Effective Go: 切片与映射]**: https://go.dev/doc/effective_go#slices

## 📝 总结

### 核心要点回顾
1. **数组是值类型**：赋值/传参复制整个数组，长度属于类型
2. **切片是视图**：共享底层数组，append 可能扩容改变地址
3. **映射必须初始化**：nil map 写入 panic；comma-ok 判断键存在
4. **结构体同理为值类型**：可比较性取决于全部字段
5. **结构体 + 切片**是Go最核心的数据建模组合

### 实践练习
- [ ] 用字面量创建一个 `map[string][]string`（如分组名→成员列表）并遍历
- [ ] 验证子切片陷阱：对 `s[1:3]` 赋值后打印原切片
- [ ] 定义 `Employee` 结构体（含姓名/年龄），创建 `[]Employee` 并统计平均年龄
- [ ] 用 `copy` 实现一个"删除切片中第 i 个元素"的函数

---

**文档状态**: 已补充共享、nil 与比较边界；运行证据仅覆盖命名实验
**最后更新**: 2026年9月
**版本**: v1.0.0

---

> 💡 **学习建议**:
> - 切片语义是Go面试高频考点，务必动手复现"共享底层数组"和"append 扩容"两个实验
> - 遇到"改了 A 却影响 B"的问题，第一时间想到共享底层数组
> - 结构体的值/指针语义将在函数和方法一文中与接收者选择呼应


## 独立实验：检查共享、空值和删除契约

上面的短片段用于解释单个操作；下面每个 Go 围栏都是一个独立 `main.go`。一次复制一块，执行 `go run main.go`，对照紧随其后的输出。[验证报告](../../shared-resources/tools/document-quality/reports/go-composite-rust-macros.md)记录这四个案例的直接正文抽取结果。

### 实验 1：限制容量与复制内部引用

<!-- verified-case: go-composite-alias -->
```go
package main

import "fmt"

func main() {
    base := []int{10, 20, 30, 40}
    part := base[:2]
    grown := append(part, 99)
    fmt.Println(base, part, grown)
    limited := base[:2:2]
    detached := append(limited, 77)
    detached[0] = 8
    fmt.Println(base, detached)

    type Profile struct { Name string; Tags []string }
    original := Profile{"Ada", []string{"go"}}
    cloned := original
    cloned.Name = "Lin"
    cloned.Tags[0] = "rust"
    fmt.Println(original.Name, original.Tags, cloned.Name)
    cloned.Tags = append([]string(nil), original.Tags...)
    cloned.Tags[0] = "python"
    fmt.Println(original.Tags, cloned.Tags)
}
```

```text
[10 20 99 40] [10 20] [10 20 99]
[10 20 99 40] [8 20 77]
Ada [rust] Lin
[rust] [python]
```

### 实验 2：copy 看长度，map 要检查存在性

nil 切片和非 nil 空切片都可以 range、len、append，但并非所有 API 都把它们当作相同值。nil map 可读、len、range、delete、clear，但新增键值会 panic。map 赋值仍共享数据；多个 goroutine 有写操作时需要同步。

<!-- verified-case: go-composite-empty -->
```go
package main

import (
    "fmt"
    "sort"
)

func main() {
    var empty []int
    allocated := make([]int, 0)
    fmt.Println(empty == nil, allocated == nil, len(empty), len(allocated))
    src := []int{1, 2, 3}
    dst := make([]int, 0, len(src))
    fmt.Println(copy(dst, src))
    dst = dst[:len(src)]
    fmt.Println(copy(dst, src), dst)
    fmt.Println(copy(dst[1:], dst[:2]), dst)

    var missing map[string]int
    value, ok := missing["Ada"]
    delete(missing, "Ada")
    fmt.Println(value, ok, len(missing))
    scores := map[string]int{"Ada": 0, "Lin": 2}
    alias := scores
    alias["Lin"] = 3
    value, ok = scores["Ada"]
    fmt.Println(value, ok, scores["Lin"])
    keys := make([]string, 0, len(scores))
    for key := range scores { keys = append(keys, key) }
    sort.Strings(keys)
    fmt.Println(keys)
}
```

```text
true false 0 0
0
3 [1 2 3]
2 [1 1 2]
0 false 0
0 true 3
[Ada Lin]
```

### 实验 3：预期失败也要有明确原因

下例只为观察语言失败而捕获 panic。真实业务优先选择合适的键和值类型，不应把无效输入捕获成成功。接口字段使比较通过编译，不保证动态比较安全。

<!-- verified-case: go-composite-panic -->
```go
package main

import "fmt"

func panics(f func()) (result bool) {
    defer func() { if recover() != nil { result = true } }()
    f()
    return false
}

func main() {
    fmt.Println(panics(func() {
        var m map[string]int
        m["x"] = 1
    }))
    fmt.Println(panics(func() {
        type Box struct{ Value any }
        b := Box{Value: []int{1}}
        _ = b == b
    }))
    fmt.Println(panics(func() {
        m := make(map[any]int)
        m[[]int{1}] = 1
    }))
}
```

```text
true
true
true
```

### 实验 4：删除一项，保持旧列表不变

这个实现返回新切片，非法索引保留原值并报错。Todo 当前只有 string/bool 字段，复制元素即满足独立修改要求；若以后加入切片字段，必须重新判断深拷贝边界。若选择原地删除，则需要左移、清零末尾槽位并缩短长度，以免长寿命底层数组保留不需要的对象引用。

<!-- verified-case: go-composite-remove -->
```go
package main

import "fmt"

type Todo struct { Title string; Done bool }

func removeAt(items []Todo, index int) ([]Todo, error) {
    if index < 0 || index >= len(items) {
        return items, fmt.Errorf("index out of range: %d", index)
    }
    result := make([]Todo, len(items)-1)
    copy(result, items[:index])
    copy(result[index:], items[index+1:])
    return result, nil
}

func main() {
    original := []Todo{{"数组", true}, {"切片", false}, {"映射", false}}
    next, err := removeAt(original, 1)
    fmt.Println(err == nil, len(original), len(next), next[1].Title)
    next[0].Title = "结构体"
    fmt.Println(original[0].Title, next[0].Title)
    unchanged, err := removeAt(original, -1)
    fmt.Println(err != nil, len(unchanged))
    _, err = removeAt(original, len(original))
    fmt.Println(err != nil)
    last, err := removeAt([]Todo{{Title: "唯一一项"}}, 0)
    fmt.Println(err == nil, len(last))
    _, err = removeAt(nil, 0)
    fmt.Println(err != nil)
}
```

```text
true 3 2 映射
数组 结构体
true 3
true
true 0
true
```

验收时尝试先预测四段输出，再改成首项删除、尾项删除和嵌套切片复制，解释变化来自长度、容量还是共享存储。不要假定扩容倍数、map 的随机性或指针字节数。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
