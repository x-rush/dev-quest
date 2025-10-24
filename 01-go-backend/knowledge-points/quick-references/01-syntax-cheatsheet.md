# Go 语法速查表

> **文档简介**: Go语言核心语法的一页速查表，包含常用语法结构和代码模式
>
> **目标读者**: Go开发者，需要快速查阅Go语法的开发者
>
> **前置知识**: 基础编程概念
>
> **预计时长**: 15分钟速查

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `knowledge-points/quick-references` |
| **难度** | ⭐ (1/5) |
| **标签** | `#语法速查` `#Go` `#快速参考` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

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
x, y := 3, 4
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

## 🔗 相关资源

- **深入学习**: [basics/02-first-program.md](../../basics/02-first-program.md)
- **相关文档**: [knowledge-points/language-concepts/01-go-keywords.md](../language-concepts/01-go-keywords.md)
- **实践参考**: [projects/01-rest-api-server.md](../../projects/01-rest-api-server.md)

---

**更新日志**: 2025年10月 - 创建Go语法速查表
