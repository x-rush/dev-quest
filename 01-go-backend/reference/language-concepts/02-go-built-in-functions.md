# Go 的 18 个内置函数：调用契约、边界与验证

> 用途：基础字典；难度：⭐，panic 与浮点边界部分为 ⭐⭐。
> 前置：[变量与常量](../../basics/03-variables-constants.md)、[复合类型](../../basics/04-composite-types.md)、[函数](../../basics/05-functions-methods.md)。
> 范围：[Go 1.27 基线](../../README.md)的全部 18 个预声明内置函数。`new(expr)` 自 Go 1.26 起可用；`clear`、`min`、`max` 自 Go 1.21 起可用。

内置函数无需 import，但它们不是关键字，也没有普通 Go 函数类型。例如不能写 `length := len` 再把 length 当作函数传递。需要这样的函数值时，应创建包装函数，如 `func(s string) int { return len(s) }`。不要定义名为 len、copy 等的局部变量，否则会遮蔽原来的内置函数。

每个完整示例独立保存为空目录中的 `main.go`，使用 Go 1.27.1 运行 `go run main.go`；后面的输出与代码一一对应。编译反例明确标注；它们失败是验收要求。实际环境、代码哈希、命令和结果见[基础参考验证记录](../../../shared-resources/tools/document-quality/reports/go-foundations-validation.md)。

## 1. 完整函数集合

下表的 T、K、V、S 是阅读用的类型占位符，调用写法不是普通函数声明。[官方内置函数规范](https://go.dev/ref/spec#Built-in_functions)定义了这些由编译器处理的操作。

| 名称 | 调用形式与返回 | 修改对象或失败行为 | 主讲节 |
| --- | --- | --- | --- |
| `append` | `append(s, x, y)` 或 `append(s, other...)` → 切片 | 可能复用底层数组，必须使用返回的切片描述 | 2 |
| `copy` | `copy(dst, src)` → 实际复制数 int | 修改 dst 长度范围内的元素，允许重叠 | 2 |
| `clear` | `clear(sliceOrMap)`，无返回 | 切片清零；map 删除全部键；nil 无操作 | 3 |
| `delete` | `delete(m, key)`，无返回 | 删除一个键；键不存在或 map 为 nil 无操作 | 3 |
| `len` | `len(value)` → int | 适用于字符串、数组、数组指针、切片、map、channel | 4 |
| `cap` | `cap(value)` → int | 适用于数组、数组指针、切片、channel；不支持 map/string | 4 |
| `make` | `make(T, size...)` → T | T 只能是切片、map、channel 或满足条件的类型参数 | 5 |
| `new` | `new(T)` 或 `new(expr)` → *T | 新变量；类型形式初始化零值，表达式形式初始化表达式值 | 5 |
| `close` | `close(ch)`，无返回 | 停止发送；重复关闭或关闭 nil 通道会 panic | 6 |
| `complex` | `complex(realPart, imagPart)` → 复数 | 对应 float32→complex64、float64→complex128 | 7 |
| `real` | `real(z)` → 实部 | 对应 complex64→float32、complex128→float64 | 7 |
| `imag` | `imag(z)` → 虚部 | 类型对应关系同 real | 7 |
| `min` | `min(x, y, ...)` → 最小值 | 至少一项；整数、浮点数或字符串；不接受切片展开 | 8 |
| `max` | `max(x, y, ...)` → 最大值 | 类型规则同 min；不是普通变长参数函数 | 8 |
| `panic` | `panic(value)`，不正常返回 | 中断正常执行并开始运行当前 goroutine 的 defer | 9 |
| `recover` | `recover()` → any | 在同 goroutine 的直接 deferred 调用中停止 panic | 9 |
| `print` | `print(values...)`，无返回 | 实现相关调试输出，不保证格式或可移植的输出流 | 10 |
| `println` | `println(values...)`，无返回 | 同 print，另有参数间分隔和行末换行 | 10 |

`unsafe.Sizeof` 等也由编译器特殊处理，但要导入 unsafe，不属于本表的 18 个预声明函数。类型转换如 `int(x)`、`string(b)` 则是转换表达式，不是遗漏的内置函数。

## 2. append 与 copy：增长、别名和独立副本

append 返回新切片描述，可能改变底层数组、长度和容量。应写 `s = append(s, value)`；不能只调用而丢弃结果。原容量足够时通常复用原数组，因此其他切片可能观察到写入；容量不足时分配新数组。增长后的具体容量属于实现选择，不能假设永远翻倍。

copy 返回 `min(len(dst), len(src))`，不会给 dst 扩长。双方元素类型需要相同；特殊形式允许把 string 复制到 `[]byte`。源、目标重叠也有明确语义。copy 是逐元素复制，不是递归深拷贝，元素内的指针或切片仍可能共享引用。

append 还有 `append([]byteValue, text...)` 的特殊形式，可直接追加字符串字节。这里只是说明形式；下面用真正的变量演示。

<!-- go-example: builtin-append-copy-seventh -->
```go
package main

import "fmt"

func main() {
    base := []int{1, 2, 3}
    short := base[:1]
    grown := append(short, 9)
    fmt.Println("shared:", base, grown)

    separate := append(base[:1:1], 8)
    separate[0] = 7
    fmt.Println("separate:", base, separate)

    empty := make([]int, 0, 5)
    fmt.Println("empty copy:", copy(empty, base))
    target := make([]int, 2)
    fmt.Println("copied:", copy(target, base), target)
    fmt.Println("overlap:", copy(base[1:], base), base)

    bytes := append([]byte("Go"), ' ')
    bytes = append(bytes, "好"...)
    text := make([]byte, 3)
    fmt.Println("text:", string(bytes), copy(text, "中"), string(text))
}
```

预期输出：

```text
shared: [1 9 3] [1 9]
separate: [1 9 3] [7 8]
empty copy: 0
copied: 2 [1 9]
overlap: 2 [1 1 9]
text: Go 好 3 中
```

`base[:1:1]` 的第三个索引把可用容量限制为 1，所以追加第 2 个元素必须分配新数组。它本身并没有立即复制第一个元素；是后续 append 需要扩容时产生了新数组。复制子切片如果要立即独立，可以分配目标并 copy，或在已掌握标准库后用 slices.Clone。

练习：把 target 长度从 2 改为 4，应得到 `copied: 3 [1 9 3 0]`。只把 empty 的容量增到 100，复制数仍为 0，因为它的长度仍为 0。

## 3. clear 与 delete：清零不等于缩短

`clear(s)` 把切片当前长度范围内的元素设为各自的零值，不改变 len、cap 或 nil 状态。其他共享这部分底层数组的切片会看到变化；长度之外的容量区域不受影响。

`clear(m)` 删除 map 的全部键；`delete(m, key)` 只删除指定键。二者没有返回值，不能据此得知删除数量；如果需要知道键是否存在，先用 comma-ok 读取，但并发访问还需要同步。这些操作不是并发安全性的替代品。

nil 切片或 nil map 上的 clear、nil map 上的 delete 都无操作。clear 不接受数组、字符串或通道，也不承诺立刻把内存归还操作系统。浮点 NaN 不等于自己，作为 map 键时普通 delete 无法按相等关系找回该键；clear 可以清空这种集合。

<!-- go-example: builtin-clear-delete -->
```go
package main

import (
    "fmt"
    "math"
)

func main() {
    all := []int{1, 2, 3}
    part := all[:2]
    clear(part)
    fmt.Println("slice:", len(part), cap(part), all)

    names := map[int]string{1: "Ada", 2: "Lin"}
    delete(names, 1)
    _, exists := names[1]
    fmt.Println("delete:", len(names), exists)
    clear(names)
    fmt.Println("map:", len(names), names == nil)

    var absent map[int]string
    delete(absent, 1)
    clear(absent)
    fmt.Println("nil:", len(absent), absent == nil)

    nan := math.NaN()
    unusual := map[float64]string{nan: "not-a-number"}
    delete(unusual, nan)
    fmt.Println("NaN delete:", len(unusual))
    clear(unusual)
    fmt.Println("NaN clear:", len(unusual))
}
```

预期输出：

```text
slice: 2 3 [0 0 3]
delete: 1 false
map: 0 false
nil: 0 true
NaN delete: 1
NaN clear: 0
```

练习：把 clear(part) 换成 `part = part[:0]`，all 仍为 `[1 2 3]`。前者改变元素；后者只改变 part 的长度描述。

## 4. len 与 cap：字节、元素与缓冲容量

len 的单位取决于输入：字符串按字节，集合按元素，通道按当前缓冲元素。UTF-8 中文通常占多个字节；`len([]rune(s))` 计算解码后的码点数，也不一定等于屏幕显示的字形数。

cap 的含义是数组长度、切片从起点到可扩展末尾的元素数，或通道缓冲容量。map 和字符串不提供 cap。nil 切片、map、channel 的 len 为 0；nil 切片和 channel 的 cap 也为 0。

长度为常量的数组或数组指针可用于常量 len/cap；在规范允许不求值的情况下，nil 数组指针也能取得长度。不要将这个特殊规则推广为“所有 nil 指针都能安全解引用”。通道 len 仅是瞬时观察，不能用 `len(ch) > 0` 判断随后接收一定不会阻塞：其他 goroutine 可能先取走消息。

<!-- go-example: builtin-len-cap -->
```go
package main

import "fmt"

func main() {
    text := "A中"
    fmt.Println("text:", len(text), len([]rune(text)))
    var slice []int
    var mapping map[string]int
    var channel chan int
    fmt.Println("nil:", len(slice), cap(slice), len(mapping), len(channel), cap(channel))
    var arrayPointer *[4]int
    fmt.Println("array pointer:", len(arrayPointer), cap(arrayPointer))
    buffered := make(chan int, 2)
    buffered <- 7
    fmt.Println("channel:", len(buffered), cap(buffered))
}
```

预期输出：

```text
text: 4 2
nil: 0 0 0 0 0
array pointer: 4 4
channel: 1 2
```

## 5. make 与 new：初始化的值和指针

make 返回指定类型本身，只支持切片、map 和 channel：

| 形式 | 初始结果 | 参数限制 |
| --- | --- | --- |
| `make([]T, n)` | 长度与容量均为 n，已有 n 个零值元素 | n 非负 |
| `make([]T, n, c)` | 长度 n、容量 c | `0 <= n <= c` |
| `make(map[K]V)` | 可写的空 map | 键类型须可比较 |
| `make(map[K]V, hint)` | 可写的空 map，提供预期条目数提示 | hint 不是桶数，不限制最终条目数；不能据此推断内存布局 |
| `make(chan T)` | 无缓冲通道 | 发送需要接收方配合 |
| `make(chan T, n)` | 缓冲容量 n、当前长度 0 | n 非负，0 等同无缓冲 |

常量形式的非法长度会在编译期报错；切片或通道的非法运行时长度导致 panic。map 的容量提示不应为负；非恒定负提示的处理不作可移植假设。内存是否放在堆上由编译器的逃逸分析决定，不能从 make/new 名字推断。

`new(T)` 返回指向 T 零值的指针。`new(map[string]int)` 因而指向 nil map，并未创建可写的 map。`new(expr)` 自 Go 1.26 起返回指向表达式值副本的指针；表达式先求值一次，无类型常量采用默认类型。不能传入无类型 nil，因为没有可推断的类型。[Go 1.26 发布说明](https://go.dev/doc/go1.26#language)说明了这一扩展。

<!-- go-example: builtin-make-new -->
```go
package main

import "fmt"

func main() {
    values := make([]int, 2, 4)
    names := make(map[string]int, 100)
    names["Ada"] = 1
    fmt.Println("make:", values, len(values), cap(values), len(names))

    zero := new(int)
    source := 7
    copied := new(source)
    source = 9
    fmt.Println("new:", *zero, *copied, source)
    flag := new(true)
    fmt.Printf("expression type: %T %v\n", flag, *flag)

    pointerToMap := new(map[string]int)
    fmt.Println("map zero:", *pointerToMap == nil)
    *pointerToMap = make(map[string]int)
    (*pointerToMap)["ready"] = 1
    fmt.Println("map initialized:", (*pointerToMap)["ready"])
}
```

预期输出：

```text
make: [0 0] 2 4 1
new: 0 7 9
expression type: *bool true
map zero: true
map initialized: 1
```

练习：若去掉 `*pointerToMap = make(map[string]int)`，随后写入会发生什么？panic，因为指针存在不代表它指向的 map 已初始化。

## 6. close：发送结束协议

close 接受双向或只发送通道；关闭只接收通道是编译错误。关闭之后，缓冲里的值仍能被接收；缓冲取空后，每次接收立即返回零值和 `ok == false`。因此，`ok == true` 表示这次确实收到了发送过的值，不能简单理解为“通道此刻仍未关闭”。

向已关闭通道发送、重复关闭或关闭有类型的 nil 通道都会 panic。`close(nil)` 本身则是编译错误，因为裸 nil 没有通道类型。关闭不是释放内存，也不要求每个通道都关闭；通常由确认“再无发送”的拥有者关闭，接收者不应抢先关闭仍有发送者的通道。

<!-- go-example: builtin-close -->
```go
package main

import "fmt"

func capture(action func()) (panicked bool) {
    defer func() {
        if recover() != nil { panicked = true }
    }()
    action()
    return
}

func main() {
    ch := make(chan int, 1)
    ch <- 0
    close(ch)
    first, firstOK := <-ch
    second, secondOK := <-ch
    fmt.Println("buffer:", first, firstOK)
    fmt.Println("drained:", second, secondOK)
    fmt.Println("close twice:", capture(func() { close(ch) }))
    fmt.Println("send closed:", capture(func() { ch <- 1 }))
    var absent chan int
    fmt.Println("close nil:", capture(func() { close(absent) }))
}
```

预期输出：

```text
buffer: 0 true
drained: 0 false
close twice: true
send closed: true
close nil: true
```

这里 capture 只供观测预期 panic，不能把“捕获重复关闭”当成正确的并发所有权设计。

## 7. complex、real、imag：类型必须对应

complex 的两个有类型参数须为相同浮点类型；float32 对应 complex64，float64 对应 complex128。无类型数值常量可以按另一个参数转换，两个无类型常量得到无类型复数常量，在 `:=` 等需要确定类型的场合默认 complex128。

real、imag 返回对应精度的浮点数。已有 int 变量不能直接当成 complex 的浮点参数，需显式转换。复数支持加减乘除和相等比较，不支持大小排序，因此也不能传给 min/max。

<!-- go-example: builtin-complex -->
```go
package main

import "fmt"

func main() {
    var a, b float32 = 3, 4
    z := complex(a, b)
    fmt.Printf("%T %v\n", z, z)
    fmt.Printf("%T %v %v\n", real(z), real(z), imag(z))
    other := complex(1, 2)
    fmt.Printf("%T %v\n", other, other)
    fmt.Println(z + complex64(other), z * complex64(other))
}
```

预期输出：

```text
complex64 (3+4i)
float32 3 4
complex128 (1+2i)
(4+6i) (-5+10i)
```

## 8. min 与 max：至少一个有序参数

min/max 接受一个或多个可比较大小的同类参数，范围为整数、浮点和字符串；不同的有类型数值不能任意混用。无类型常量按运算符相同的类型规则处理，例如 `max(1, 2.5)` 可推导为浮点常量。只有一个参数时返回该参数。全部参数为常量时结果可用于 const。

它们没有 slice 展开形式，也不接受零参数。对切片可在检查非空后使用标准库 slices.Min/Max，或从第一个元素开始循环比较；不能把初始最小值写死为 0，否则全正数集合会得到错误结果。

浮点 NaN 会传播；有符号零也有规定：min 将负零视为更小，max 将正零视为更大。字符串按字节字典序比较，不按当地语言的词典规则排列。[官方极值规则](https://go.dev/ref/spec#Min_and_max)适用于这些边界。

<!-- go-example: builtin-min-max -->
```go
package main

import (
    "fmt"
    "math"
    "slices"
)

func main() {
    fmt.Println(min(8, 3, 5), max(8, 3, 5), min(7))
    fmt.Println(min("Go", "Rust"), max("Go", "Rust"))
    values := []int{8, 3, 5}
    if len(values) > 0 { fmt.Println("slice:", slices.Min(values)) }
    fmt.Println("NaN:", math.IsNaN(min(1.0, math.NaN())))
    negativeZero := math.Copysign(0, -1)
    positiveZero := 0.0
    fmt.Println("zero signs:",
        math.Signbit(min(negativeZero, positiveZero)),
        math.Signbit(max(negativeZero, positiveZero)))
}
```

预期输出：

```text
3 8 7
Go Rust
slice: 3
NaN: true
zero signs: true false
```

编译反例：`go build main.go` 必须失败，错误原因是内置 min 不支持切片展开。修正版就是上例中先检查长度再调用 slices.Min 的部分。

<!-- go-compile-error: builtin-min-slice | invalid use of \.\.\. -->
```go
package main

func main() {
    values := []int{8, 3, 5}
    _ = min(values...)
}
```

## 9. panic 与 recover：不要把失败吞成成功

普通的非法用户输入、文件不存在等预期失败通常返回 error。panic 表示当前流程不能继续，开始在当前 goroutine 向外展开调用栈并运行 defer；若未恢复，最终会终止程序。

recover 必须由同一个 goroutine 中正在运行的 deferred 函数直接调用，才可能恢复正在发生的 panic。普通调用会得到 nil；在 deferred 函数中再调用另一个辅助函数，由辅助函数去 recover，也不能恢复。成功恢复后，不会回到 panic 那一行继续执行，而是从登记该 defer 的函数返回给调用者。

若恢复后要返回错误，必须更新实际返回结果。下面使用命名的 err：只打印日志却不赋值，会令调用者误以为返回 nil 就是成功。本例用于解释库边界的隔离；能直接返回 error 的校验函数不必先 panic 再恢复。

<!-- go-example: builtin-panic-recover -->
```go
package main

import "fmt"

func divide(a, b int) int {
    if b == 0 { panic("division by zero") }
    return a / b
}

func guarded(a, b int) (result int, err error) {
    defer func() {
        if problem := recover(); problem != nil {
            err = fmt.Errorf("calculation failed: %v", problem)
        }
    }()
    result = divide(a, b)
    return result, nil
}

func main() {
    result, err := guarded(8, 2)
    fmt.Println("normal:", result, err)
    result, err = guarded(8, 0)
    fmt.Println("failure:", result, err)
    fmt.Println("outside panic:", recover() == nil)
}
```

预期输出：

```text
normal: 4 <nil>
failure: 0 calculation failed: division by zero
outside panic: true
```

Go 1.21 起默认行为下，`panic(nil)` 也会提供非 nil 的恢复值（运行时的 PanicNilError），不要用它表示“没有错误”。recover 也不能捕获另一 goroutine 的 panic；故障隔离必须安装在对应 goroutine 内。

练习：若删除 `err = fmt.Errorf(...)` 只保留一次打印，guarded(8, 0) 会返回 `0, nil`。这会把失败误报为成功。正确做法是返回明确错误，或在不具备恢复能力时让 panic 继续传播。

## 10. print 与 println：只把它们当调试辅助

print 和 println 属于内置调试设施，接受的类型与具体格式依赖实现；不是 fmt 的精简兼容版本。println 会在参数间加入分隔并追加换行，但浮点、复合值等格式不应当作为跨平台协议或测试契约。需要确定的终端输出用 fmt，需要结构化运行记录用 log/slog。

下面是唯一不把内置调试输出写成稳定 stdout 契约的示例。Go 1.27.1 的本次 Linux 实现把 `debug: 2` 写入 stderr，并带换行；语言层不承诺该输出流。正文里的稳定输出由 fmt 给出。

<!-- go-example: builtin-debug -->
<!-- go-stderr: debug: 2 -->
```go
package main

import "fmt"

func main() {
    print("debug:")
    println(" 2")
    fmt.Println("stable: 2")
}
```

stdout 预期输出：

```text
stable: 2
```

## 11. 复习与迁移到实际项目

| 场景 | 先回答的问题 | 合适做法 |
| --- | --- | --- |
| 从数据库结果组装切片 | 知道条目数还是只知道上界？ | 知道确切长度可 make 长度后按索引写；只预留容量则 make 长度 0 再 append |
| 把缓存中的列表返回调用者 | 是否允许对方改变共享底层数据？ | 需要隔离就复制；嵌套引用还要明确复制深度 |
| 清空一批待办 | 需要保留切片长度，还是移除集合元素？ | clear(slice) 清零；缩短切片改变逻辑长度；clear(map) 删除条目 |
| 并发任务结束 | 谁能保证没有后续发送？ | 由拥有发送完成条件的一方关闭，接收方按 ok 或 range 判断结束 |
| 为可选字段提供指针 | 需要零值还是给定值？ | new(T) 与 new(expr) 按语义选择；不要把 map 指针误当可写 map |
| 捕获库回调 panic | 调用方能否获知失败？ | 在明确边界设置 defer/recover，返回错误并保持可诊断信息 |

继续完成[标准库待办命令行项目](../../projects/00-stdlib-todo-cli.md)，将 append、len、map 和错误返回组合起来；集合深入见[切片语义](10-slice-semantics.md)与[map 语义](11-map-semantics.md)。

## 阅读导航

[关键字与全部预声明标识符](01-go-keywords.md) · [defer、panic 与 recover](14-defer-panic-recover.md) · [标准库集合工具](../library-guides/13-slices-maps.md) · [模块学习路线](../../LEARNING_GUIDE.md)
