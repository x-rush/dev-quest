# Go 的 25 个关键字与预声明标识符

> 用途：基础字典；难度：⭐，泛型与迭代器部分为 ⭐⭐。
> 前置：[首个程序](../../basics/02-first-program.md)、[变量和类型](../../basics/03-variables-constants.md)。
> 适用范围：模块 [Go 1.27 基线](../../README.md)。本文核对 25 个保留关键字和全部预声明标识符；内置函数的调用契约见[内置函数参考](02-go-built-in-functions.md)。

关键字决定程序的语法结构，不能重新命名。例如 `func` 开始函数声明，`return` 结束当前函数。`len`、`int`、`nil` 是预声明标识符，可被局部声明遮蔽，但遮蔽它们会降低可读性。`fmt.Println` 来自导入的标准库，既不是关键字，也不是无需导入的内置函数。

以下每个“完整示例”单独保存为空目录中的 `main.go`，使用 Go 1.27.1 运行 `go run main.go`。不要把多个示例拼成一个文件。代码后的输出逐行对应该程序；有意失败的代码单独标为“编译反例”。实际命令、内容哈希与结果见[基础参考验证记录](../../../shared-resources/tools/document-quality/reports/go-foundations-validation.md)。

## 1. 关键字覆盖表

下表是有限的 25 项集合，来源为[官方关键字定义](https://go.dev/ref/spec#Keywords)。单元格中的语法是阅读提示，详细机制与运行示例见后续各节。

| 关键字 | 写在哪里、解决什么问题 | 必须理解的边界 | 主讲节 |
| --- | --- | --- | --- |
| `package` | 文件开头声明所属包，如 `package main` | 名字是单个标识符，不能写导入路径 | 2 |
| `import` | 包声明之后引入其他包 | 导入路径与本地名字不同；普通导入必须使用 | 2 |
| `var` | 声明可修改的变量 | 未显式初始化时得到类型零值；`:=` 只在函数中使用 | 3 |
| `const` | 声明编译期常量 | 不能把切片、map 或任意函数结果作为常量 | 3 |
| `type` | 定义类型或声明类型别名 | `type ID int` 是新类型；`type ID = int` 是别名 | 3 |
| `struct` | 组合有名称的字段 | 赋值复制结构体，但引用其他数据的字段仍可能共享数据 | 3 |
| `interface` | 声明方法能力或泛型约束 | 方法集满足即可实现；含类型项的非基本接口只作约束 | 3 |
| `func` | 声明函数、方法或函数值 | Go 不按参数列表重载同名函数 | 3 |
| `return` | 返回结果或提前退出当前函数 | 先确定返回值，再运行 defer，最后回到调用者 | 3、6 |
| `if` | 按布尔条件选择分支 | 不把数字自动当布尔值；初始化变量仅在整条 if 中可见 | 4 |
| `else` | 接续 if 的未满足分支 | 通常与前一个 `}` 同一行，避免自动插入分号 | 4 |
| `switch` | 在多个值、条件或动态类型之间选择 | 是语句；普通分支结束自动退出 switch | 4 |
| `case` | 定义 switch 分支或 select 通信分支 | switch 比较条件；select 选择可进行的通信 | 4、7 |
| `default` | switch 无匹配或 select 无就绪时的分支 | select 带 default 就不会等候；空转循环会耗 CPU | 4、7 |
| `for` | 循环、条件重复、遍历 | Go 没有 while 关键字；无限循环应有明确退出条件 | 5 |
| `range` | 配合 for 获取迭代值 | 字符串索引是字节偏移；map 顺序不保证 | 5 |
| `break` | 退出最内层 for、switch 或 select | 不会自动退出外层循环；标签可指定外层目标 | 4、5 |
| `continue` | 开始下一轮 for | 有标签时目标必须是外层 for | 5 |
| `fallthrough` | 执行表达式 switch 的下一分支体 | 不检查下一条件；不能用于类型 switch 或 select | 4 |
| `defer` | 登记在当前函数返回前执行的调用 | 当场求参数；多个调用后进先出；不是代码块退出时执行 | 6 |
| `go` | 并发启动函数调用 | 不自动等候完成，也不把函数返回值传回调用者 | 7 |
| `chan` | 声明双向或单向通道类型 | nil 通道的收发永远不能完成 | 7 |
| `select` | 在通道收发中选择一个可进行的操作 | 多个就绪分支不按源码先后选取 | 7 |
| `map` | 声明键值集合类型 | 键必须可比较；nil map 可读但写入会 panic | 8 |
| `goto` | 跳到当前函数中的标签 | 不能越过变量声明，使变量未经初始化就进入作用域 | 9 |

## 2. package 与 import：名字、目录和依赖

一个 Go 源文件只有一个包声明。声明前可以有注释或构建约束；其后是导入，再后是声明。同一目录的普通 Go 文件通常属于同一个包。`main` 包中无参数、无返回值的 `main` 函数是可执行程序入口；其他包提供可复用代码。

假设模块路径为 `example.com/shop`，子目录为 `database/mysql`，该目录可以声明 `package mysql`，调用者导入 `"example.com/shop/database/mysql"`。`package database/mysql` 是语法错误：目录路径属于 import，而不是 package。

普通导入名默认由被导入包的 package 声明决定；可用别名覆盖。`import _ "image/png"` 只触发包初始化，例如注册 PNG 解码器，不引入可用名字。`import . "fmt"` 将导出的名字直接引入当前文件，容易冲突，初学代码采用明确的包名前缀。Go Modules 项目应通过模块路径导入自己的包，不使用 `"./utils"` 这样的相对导入。

完整示例：别名只影响当前文件如何引用包，不会改写标准库名称。

<!-- go-example: keyword-package -->
```go
package main

import output "fmt"

func main() {
    output.Println("package name is not an import path")
}
```

预期输出：

```text
package name is not an import path
```

自测：把调用改成 `fmt.Println` 会怎样？会编译失败，因为当前文件引入的名字是 `output`。改回 `import "fmt"` 或恢复 `output.Println` 即可。

## 3. var、const、type、struct、interface、func、return

`var title string` 创建字符串零值 `""`；`var count = 3` 根据表达式推导类型。函数中的 `count := 3` 是短变量声明，同一作用域的左侧必须至少有一个新非空白变量。`const` 的值在编译期确定，可以不指定类型；`iota` 从常量组的第 0 条声明开始递增，下一组重新计数。

`type ID int` 创建与 int 不同的命名类型，便于表达业务含义，必要时显式转换；`type Label = string` 让 Label 成为 string 的另一个名字。`struct` 定义字段，`func (u User) Name() string` 给 User 定义值接收者方法；指针接收者 `*User` 可修改原值，其方法集与 User 不完全相同。

接口将“调用方需要什么能力”表示成方法集合。`interface{ Name() string }` 要求一个方法；实现者不写 implements。接口值包含动态类型和值，因此装入带类型的 nil 指针后，接口自身未必等于 nil，详见 [nil 语义](15-nil-semantics.md)。

`func` 也可以创建匿名函数并捕获外层变量。`return` 的结果必须符合函数声明；命名返回参数是普通局部变量，裸 `return` 返回其当前值。短函数一般显式写返回表达式，方便读者查明结果来源。

完整示例把声明、方法、接口和函数值放进一个真正可运行的程序：

<!-- go-example: keyword-declarations -->
```go
package main

import "fmt"

type ID int
type Label = string

type User struct {
    ID ID
    Title Label
}

func (u User) Name() string { return u.Title }

type Named interface {
    Name() string
}

const (
    pending = iota
    active
)

func doubled(x int) (result int) {
    result = x * 2
    return
}

func main() {
    var empty string
    var user = User{ID: ID(7), Title: "Ada"}
    var named Named = user
    fmt.Printf("%q %d %d %s\n", empty, pending, active, named.Name())
    factor := 3
    multiply := func(x int) int { return x * factor }
    fmt.Println(doubled(4), multiply(4))
}
```

预期输出：

```text
"" 0 1 Ada
8 12
```

接口也可限定类型参数，如 `interface{ ~int | ~int64 }`；`~` 表示底层类型。这种包含类型项的非基本接口只能用作约束，不能声明普通接口变量。[泛型参考](09-generics.md)进一步解释类型集合。Go 1.27 允许具体类型的方法声明自己的类型参数，但接口方法仍不能声明类型参数；不要把旧版本的“所有方法都不能有独立类型参数”套用到本基线。[官方语言变更](https://go.dev/doc/go1.27#language)说明了这一边界。

自测：将 `Name` 改成指针接收者 `func (u *User) Name() string` 后，`var named Named = user` 是否仍成立？不成立，改为 `&user`；自动取地址的方法调用便利规则，不等于值的方法集增加了指针方法。

## 4. if、else、switch、case、default、fallthrough

`if` 接收布尔表达式；可先执行一条初始化语句，如 `if n := len(title); n == 0`。这里的 n 在 if 和 else 中可见，离开整条语句后不可见。Go 根据换行插入分号，因此通常写 `} else {`。

表达式 switch 先确定被比较的值，再按顺序寻找匹配 case；没有表达式时相当于比较 true，因此可以分类数值区间。每个普通 case 结束就退出 switch，不需要习惯性加 break。`default` 在没有任何 case 匹配时执行，不要求写在最后。类型 switch 的 `v := value.(type)` 检查接口的动态类型；这种 `.(type)` 形式只用于类型 switch。

`fallthrough` 必须是表达式 switch 某个非末尾分支的最后一条非空语句，它执行下一个分支体而不测试条件；不能写在 if 的嵌套块里，也不能用于类型 switch 或 select。

<!-- go-example: keyword-decisions -->
```go
package main

import "fmt"

func classify(score int) string {
    if score < 0 || score > 100 {
        return "invalid"
    } else if score == 100 {
        return "perfect"
    }
    switch {
    case score >= 80:
        return "pass"
    default:
        return "retry"
    }
}

func main() {
    fmt.Println(classify(-1), classify(85), classify(100))
    switch n := 2; n {
    case 2:
        fmt.Println("matched 2")
        fallthrough
    case 99:
        fmt.Println("ran body of 99")
    }
    var value any = "hello"
    switch v := value.(type) {
    case string:
        fmt.Println("string bytes:", len(v))
    case int:
        fmt.Println("integer:", v)
    default:
        fmt.Println("other")
    }
}
```

预期输出：

```text
invalid pass perfect
matched 2
ran body of 99
string bytes: 5
```

练习：去掉 fallthrough 后输出如何变化？只少一行 `ran body of 99`。把 classify 的分数改为 79，应得到 retry；改为 101，应得到 invalid。

## 5. for、range、break、continue

`for i := 0; i < n; i++` 分别表达初始化、继续条件和轮次更新；`for condition` 只保留条件；`for {}` 持续执行直到 break、return 或其他终止行为。`continue` 结束本轮，三段式 for 随后执行更新语句；`break` 退出最内层 for、switch 或 select。循环内的 switch 中若想退出外层循环，需要给循环加标签，例如 `break Outer`。

| range 输入 | 得到的迭代值 | 零值和边界 |
| --- | --- | --- |
| 数组、数组指针、切片 | 索引、元素副本 | nil 切片迭代 0 次；修改副本不会替换原元素 |
| 字符串 | 字节偏移、rune 码点 | 无效 UTF-8 产生替代码点；rune 不是用户可见字形 |
| map | 键、值 | 顺序不保证；遍历中新增项可能被访问，也可能不被访问 |
| 可接收 channel | 一项：接收的值 | 取完已发送值并关闭后结束；nil channel 永久等待 |
| 整数，Go 1.22 起 | 一项：从 0 到 n−1 | n≤0 时不执行；不能提供第二个迭代变量 |
| 迭代器函数，Go 1.23 起 | 由 yield 产生 0、1 或 2 项 | 支持 `func(func() bool)`、`func(func(V) bool)`、`func(func(K,V) bool)` |

迭代器获得 yield 回调；每次调用产生一轮值。循环 break 后 yield 返回 false，迭代器必须停止，不能继续调用。有关迭代与变量作用域的准确约定见[官方 for 语句规范](https://go.dev/ref/spec#For_statements)。

Go 1.22 起，循环中用 `:=` 声明的迭代变量每轮各有一份；闭包不再自动共享同一个这样的变量。使用预先声明的变量和 `=` 赋值仍会共享。语言语义还受项目 `go.mod` 的 go 指令影响，不应只看本机编译器版本。

<!-- go-example: keyword-loops -->
```go
package main

import "fmt"

func firstThree(yield func(int) bool) {
    for i := range 3 {
        if !yield(i) {
            return
        }
    }
}

func main() {
    sum := 0
Outer:
    for i := 0; i < 3; i++ {
        for j := 0; j < 3; j++ {
            if i == 1 { break Outer }
            if j == 1 { continue }
            sum += j
        }
    }
    fmt.Println("sum:", sum)

    items := []int{1, 2}
    for _, item := range items { item *= 10 }
    fmt.Println("copy:", items)
    for i := range items { items[i] *= 10 }
    fmt.Println("index:", items)
    for offset, r := range "A中" { fmt.Printf("%d:%c\n", offset, r) }

    fresh := []func() int{}
    for i := range 3 {
        fresh = append(fresh, func() int { return i })
    }
    shared := []func() int{}
    var j int
    for j = range 3 {
        shared = append(shared, func() int { return j })
    }
    fmt.Println("fresh:", fresh[0](), fresh[1](), fresh[2]())
    fmt.Println("shared:", shared[0](), shared[1](), shared[2]())
    values := []int{}
    for v := range firstThree {
        if v == 2 { break }
        values = append(values, v)
    }
    fmt.Println("iterator:", values)
}
```

预期输出（`A中` 的第二个字符从字节 1 开始；中文字符自身占 3 字节）：

```text
sum: 2
copy: [1 2]
index: [10 20]
0:A
1:中
fresh: 0 1 2
shared: 2 2 2
iterator: [0 1]
```

自测：把共享变量循环改成 `for j = 0; j < 3; j++`，三个闭包会返回 3；这是循环完成后共享 j 的值，而不是“闭包总是返回 3”。

## 6. defer 与 return：先求值，再清理

遇到 defer 时，函数值和实参立即求值，调用本身登记到当前函数退出之前。多个 defer 按后登记先执行的顺序运行。匿名函数捕获的变量通常在执行匿名函数时读取，因此与“把变量当实参传入”不同。

return 先把表达式赋给结果位置，再运行 defer。命名结果可被 defer 修改；普通局部变量被修改，不会回头改变已经复制的匿名结果。原文中“未命名结果也被 defer 改成 2”的解释不成立。

<!-- go-example: keyword-defer -->
```go
package main

import "fmt"

func unnamed() int {
    result := 1
    defer func() { result *= 2 }()
    return result
}

func named() (result int) {
    defer func() { result *= 2 }()
    return 1
}

func showOrder() {
    x := 1
    defer fmt.Println("argument:", x)
    defer func() { fmt.Println("closure:", x) }()
    x = 2
    fmt.Println("body:", x)
}

func main() {
    fmt.Println(unnamed(), named())
    showOrder()
}
```

预期输出：

```text
1 2
body: 2
closure: 2
argument: 1
```

用于资源清理时，应先确认资源取得成功，再登记关闭；写文件的 Close 错误可能影响最终结果，不能一概忽略。循环里累积 defer 会把资源一直留到整个函数返回，可以把一次处理提取到函数。panic 展开期间同样执行 defer；`os.Exit` 不执行 defer。继续阅读 [defer、panic 与 recover](14-defer-panic-recover.md)。

## 7. go、chan、select：并发、通信与完成条件

`go f(x)` 在当前 goroutine 求得函数与实参后，启动并发调用。它不能保证对方什么时候运行；main 返回时程序结束。用消息、WaitGroup 或其他同步机制等待工作完成，不能用 Sleep 猜测任务耗时。

`chan T` 双向，`chan<- T` 只发送，`<-chan T` 只接收。方向限制的是拿到该值的代码能做什么，不是产生两个独立通道。发送与接收拷贝元素值，元素内含切片等引用时仍需考虑共享数据。

select 可以等待发送或接收。多个分支同时就绪时随机选择一个，不保证源码中的第一项优先。nil 通道可禁用某个分支；关闭的通道在缓冲数据取完后一直可以接收零值和 false。若在循环里处理多个通道，处理完关闭事件后应退出或将对应通道变量设为 nil，避免空转。

<!-- go-example: keyword-concurrency -->
```go
package main

import "fmt"

func produce(out chan<- int) {
    defer close(out) // 只有这个生产者负责发送和关闭。
    for i := range 3 { out <- i * i }
}

func main() {
    out := make(chan int)
    go produce(out)
    values := []int{}
    for v := range out { values = append(values, v) }
    fmt.Println("values:", values)

    var disabled <-chan int
    select {
    case <-disabled:
        fmt.Println("unreachable")
    default:
        fmt.Println("nothing ready")
    }
    select {
    case v, ok := <-out:
        fmt.Println("closed:", v, ok)
    default:
        fmt.Println("unreachable")
    }
}
```

预期输出：

```text
values: [0 1 4]
nothing ready
closed: 0 false
```

练习：删除 produce 中的 close，会发生什么？main 收到三个值后仍在等待第四次接收，不能正常结束。该例说明通道关闭是协议里的完成信号；更复杂的生产者数量与取消机制见[并发基础](../../basics/07-concurrency-basics.md)。

## 8. map：零值、缺失键与写入

`map[K]V` 将可比较的 K 映射为 V。切片、map 和函数类型不能直接做键；接口作为键时，其动态值也必须可比较，否则操作可能 panic。

读取不存在的键返回 V 的零值，因此判断是否存在应使用 `value, ok := m[key]`。nil map 可查询、求长度、delete 和 clear，但写入需要先 make 或使用 map 字面量。map 赋值共享同一集合，普通 map 也不提供并发写入保护。

<!-- go-example: keyword-map -->
```go
package main

import "fmt"

func main() {
    var scores map[string]int
    value, ok := scores["Ada"]
    fmt.Println(value, ok, len(scores))
    scores = make(map[string]int)
    scores["Ada"] = 0
    value, ok = scores["Ada"]
    fmt.Println(value, ok, len(scores))
    alias := scores
    alias["Ada"] = 9
    fmt.Println(scores["Ada"])
}
```

预期输出：

```text
0 false 0
0 true 1
9
```

自测：为什么第二行值仍为 0、ok 却是 true？集合已保存这个键，保存的值刚好也是零。详见 [map 语义](11-map-semantics.md)。

## 9. goto：作用域仍然有效

goto 只能跳到同一函数内的标签，不能跨函数、不能跳入其他块，也不能跳过声明让一个变量未经初始化就进入作用域。资源清理通常用 defer，循环退出通常用 break；只有更直接表达控制流程时才使用 goto。

<!-- go-example: keyword-goto -->
```go
package main

import "fmt"

func main() {
    n := 0
Again:
    fmt.Println(n)
    n++
    if n < 2 { goto Again }
}
```

预期输出：

```text
0
1
```

编译反例，单独保存为 main.go 后执行 `go build main.go`，预期因跳过 x 的声明而失败：

<!-- go-compile-error: keyword-goto-scope | jumps over declaration -->
```go
package main

func main() {
    goto Done
    x := 1
Done:
    println(x)
}
```

修正时把 `x := 1` 放到 goto 之前。不能仅因为标签在文件后面，就认为跳转可以跳过所有声明。

## 10. 全部预声明标识符：不是更多关键字

下列 44 个名称来自[预声明集合](https://go.dev/ref/spec#Predeclared_identifiers)。这里的类别与官方区分一致。它们在 universe 作用域中可用；空白标识符 `_` 不属于此集合，它用于丢弃值或避免引入名字，不能拿来读取值。

| 类别 | 完整名称集合 | 语义与边界 |
| --- | --- | --- |
| 布尔与字符串 | `bool string` | bool 只有 true/false；string 是不可变字节序列，索引得到 byte |
| 有符号整数 | `int int8 int16 int32 int64` | int 宽度由实现选择 32 或 64 位；固定宽度类型不能靠名字相近直接赋值 |
| 无符号整数 | `uint uint8 uint16 uint32 uint64 uintptr` | uintptr 是整数，不会保持对象存活；不能当作普通指针替代品 |
| 数值别名 | `byte rune` | byte 是 uint8 别名，rune 是 int32 别名；不是额外的新类型 |
| 浮点与复数 | `float32 float64 complex64 complex128` | 浮点会舍入；complex64 的两部分各为 float32，complex128 各为 float64 |
| 接口和约束 | `any error comparable` | any 是 interface{} 别名；error 要求 Error() string；comparable 只能作类型约束 |
| 常量 | `true false iota` | iota 只能用于常量声明，从常量组起点逐条递增 |
| 零值标识符 | `nil` | 用于指针、函数、切片、map、channel、接口的零值；`var x = nil` 无法推断类型，`nil == nil` 也不成立 |
| 内置函数 | `append cap clear close complex copy delete imag len make max min new panic print println real recover` | 共 18 个；只能在调用表达式中使用，不能像普通函数那样赋给变量；逐项见[内置函数](02-go-built-in-functions.md) |

上述 22 个类型名、3 个常量名、nil 和 18 个函数名合计 **44** 个预声明标识符。覆盖记录按名字逐项核对，不把别名去重，也不把 unsafe 包函数算入无需导入的集合。

`any` 允许任意类型，但不保证其中的动态值可比较。`comparable` 用于 map 键或泛型相等比较；当类型实参是 any 等接口类型时，类型检查不代表所有运行时动态值都可比较。例如装入切片后比较接口仍会 panic。

<!-- go-example: keyword-predeclared -->
```go
package main

import "fmt"

type titleError string

func (e titleError) Error() string { return string(e) }

func unique[T comparable](values []T) []T {
    seen := make(map[T]bool)
    result := []T{}
    for _, value := range values {
        if !seen[value] {
            seen[value] = true
            result = append(result, value)
        }
    }
    return result
}

func main() {
    var octet byte = 65
    var codePoint rune = '中'
    var unknown any = codePoint
    var err error = titleError("empty title")
    var missing *int
    fmt.Printf("%T %T %T\n", octet, codePoint, unknown)
    fmt.Println(err.Error(), missing == nil, true && !false)
    fmt.Println(unique([]string{"Go", "Go", "SQL"}))
}
```

预期输出：

```text
uint8 int32 int32
empty title true true
[Go SQL]
```

练习：用 `[]int{2, 1, 2}` 调用 unique，结果应为 `[2 1]`，因为程序保留首次出现顺序；它没有依赖 map 的遍历顺序。

## 阅读导航

[内置函数契约与边界](02-go-built-in-functions.md) · [数据类型](04-go-data-types.md) · [泛型](09-generics.md) · [标准库小项目](../../projects/00-stdlib-todo-cli.md) · [模块学习路线](../../LEARNING_GUIDE.md)
