# Go 语法速查表

> **文档简介**: Go语言核心语法的一页速查表，包含常用语法结构和代码模式
>
> **目标读者**: Go开发者，需要快速查阅Go语法的开发者
>
> **前置知识**: 基础编程概念
>
> **预计时长**: 15分钟速查

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `reference/quick-references` |
| **难度** | ⭐ (1/5) |
| **标签** | `#语法速查` `#Go` `#快速参考` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 基础语法

### 包声明和导入
```go
package main

import "fmt"
import (
    "os"
    "strings"
)
```

### 变量声明
```go
// 基本声明
var name string = "John"
var age int = 30

// 短声明
name := "Jane"
age := 25

// 多变量声明
var x, y int = 1, 2
x, y = 3, 4 // 已有变量赋值；若要演示 :=，必须放到独立示例或包含新变量
```

### 常量声明
```go
const Pi = 3.14159
const (
    StatusOK = 200
    StatusNotFound = 404
)
```

## 🎯 函数定义

### 基本函数
```go
func add(a, b int) int {
    return a + b
}

// 多返回值
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero")
    }
    return a / b, nil
}
```

### 方法定义
```go
type Rectangle struct {
    width, height float64
}

func (r Rectangle) Area() float64 {
    return r.width * r.height
}

// 指针接收者
func (r *Rectangle) SetWidth(width float64) {
    r.width = width
}
```

## 🎯 结构体和接口

### 结构体定义
```go
type Person struct {
    Name string
    Age  int
    Email string
}

// 结构体字面量
p := Person{
    Name:  "Alice",
    Age:   30,
    Email: "alice@example.com",
}
```

### 接口定义
```go
type Writer interface {
    Write([]byte) (int, error)
}

type Reader interface {
    Read([]byte) (int, error)
}

type ReadWriter interface {
    Reader
    Writer
}
```

## 🎯 错误处理

### 基本错误处理
```go
result, err := someFunction()
if err != nil {
    log.Fatal(err)
}

// 自定义错误
func validateAge(age int) error {
    if age < 0 {
        return fmt.Errorf("age cannot be negative: %d", age)
    }
    return nil
}
```

## 🎯 并发编程

### Goroutine
```go
go func() {
    fmt.Println("Hello from goroutine")
}()

// 匿名函数
go func(name string) {
    fmt.Printf("Hello, %s\n", name)
}("World")
```

### Channel
```go
// 创建channel
ch := make(chan int)
ch := make(chan string, 10) // 带缓冲

// 发送和接收
ch <- 42
value := <-ch

// 关闭channel
close(ch)
```

### Select语句
```go
select {
case msg1 := <-ch1:
    fmt.Println("Received", msg1)
case msg2 := <-ch2:
    fmt.Println("Received", msg2)
case <-time.After(time.Second):
    fmt.Println("Timeout")
}
```

<!-- full-library-explanation -->
## 查到语法后，先确认作用域与值语义

速查页的代码块是各自独立的语法示意，不应把所有声明直接粘进一个函数。:= 只能在函数内部使用，且同一作用域的左侧至少有一个新的非空白变量；已有变量再次赋值用 =。内层代码块可以声明同名变量并遮蔽外层值，但这往往让错误处理难以理解。例如 if 中的 err := 只存在于该 if 的作用域，不能据此判断外层 err 已更新。

阅读任何集合操作时再问两件事：是否改变长度，是否共享底层数据。append 要接收返回值，map 读取不存在键会返回零值，若需要区分“键不存在”和“值就是零”，使用 value, ok。make 创建可用的 slice/map/channel，new 只分配并返回零值的指针；new(map[K]V) 并不会自动创建可写入的 map。

### 可复现速查：`map` 读取与 `append` 返回值

下面的程序把两个边界放在一起：`count["missing"]` 和已有键的零值都读取为 `0`，必须看第二个返回值 `ok`；`append` 的结果必须重新赋回变量。示例只使用标准库，适合作为遇到集合行为疑问时的最小复现模板。

<!-- doc-verify:go-cheatsheet-map-append-boundaries -->
```go
package main

import "fmt"

func main() {
	count := map[string]int{"zero": 0}
	zero, zeroOK := count["zero"]
	missing, missingOK := count["missing"]
	items := []int{1}
	items = append(items, 2)
	fmt.Printf("zero=%d,%t missing=%d,%t items=%v\n", zero, zeroOK, missing, missingOK, items)
}
```

预期输出：

```text
zero=0,true missing=0,false items=[1 2]
```

练习：先声明 x:=1，在内层花括号里 x:=2，离开后外层应仍为 1；将内层 := 改为 = 后外层应为 2。再对 nil map 分别读取和写入，读取得到零值、写入会 panic；用 make 初始化后才可写。遇到解释不清的结果，转到对应语言语义条目，不要仅靠记住代码形状。

## 🔗 相关资源

- **深入学习**: [basics/02-first-program.md](../../basics/02-first-program.md)
- **相关文档**: [reference/language-concepts/01-go-keywords.md](../language-concepts/01-go-keywords.md)
- **实践参考**: [projects/01-rest-api-server.md](../../projects/01-rest-api-server.md)

---

**更新日志**: 2026年9月 - 创建Go语法速查表


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
