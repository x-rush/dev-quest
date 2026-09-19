# Go 面向对象概念速查手册

> **文档简介**: Go语言中面向对象编程概念的完整参考手册，包含结构体、接口、组合等核心概念
>
> **目标读者**: Go开发者，需要快速查阅Go面向对象概念的开发者
>
> **前置知识**: Go语言基础语法、结构体基础
>
> **预计时长**: 30分钟速查

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `reference/language-concepts` |
| **难度** | ⭐⭐⭐ (3/5) |
| **标签** | `#面向对象` `#结构体` `#接口` `#组合` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 快速索引

### 核心概念
- [结构体定义](#结构体定义)
- [方法定义](#方法定义)
- [接口定义](#接口定义)
- [组合模式](#组合模式)

### Go特色
- [值接收者vs指针接收者](#值接收者vs指针接收者)
- [接口隐式实现](#接口隐式实现)
- [空接口](#空接口)

## 📖 核心概念

### 结构体定义
```go
// 基本结构体
type Person struct {
    Name string
    Age  int
    Email string
}

// 带标签的结构体
type User struct {
    ID       int    `json:"id"`
    Username string `json:"username" db:"username"`
    Password string `json:"-"` // 不序列化
}
```

### 方法定义
```go
// 值接收者方法
func (p Person) GetName() string {
    return p.Name
}

// 指针接收者方法
func (p *Person) SetName(name string) {
    p.Name = name
}

// 构造函数
func NewPerson(name string, age int) *Person {
    return &Person{
        Name: name,
        Age:  age,
    }
}
```

### 接口定义
```go
// 基本接口
type Writer interface {
    Write([]byte) (int, error)
}

// 多方法接口
type Reader interface {
    Read([]byte) (int, error)
    Close() error
}

// 组合接口
type ReadWriter interface {
    Reader
    Writer
}
```

### 组合模式
```go
// 结构体嵌套
type Address struct {
    Street  string
    City    string
    Country string
}

type Person struct {
    Name    string
    Age     int
    Address Address // 组合
}

// 接口组合
type Logger interface {
    Log(message string)
}

type Database interface {
    Query(sql string) Result
}

type Service struct {
    Logger
    Database
}
```

## 📖 Go特色

### 值接收者vs指针接收者
```go
type Counter struct {
    count int
}

// 值接收者 - 不修改原始结构体
func (c Counter) Value() int {
    return c.count
}

// 指针接收者 - 修改原始结构体
func (c *Counter) Increment() {
    c.count++
}
```

### 接口隐式实现
```go
type Writer interface {
    Write([]byte) (int, error)
}

// 自动实现Writer接口
type FileWriter struct {
    file *os.File
}

func (fw FileWriter) Write(data []byte) (int, error) {
    return fw.file.Write(data)
}
```

### 空接口
```go
// 空接口可以接受任何类型
func PrintAnything(value interface{}) {
    fmt.Printf("Value: %v, Type: %T\n", value, value)
}

// 类型断言
func ProcessData(data interface{}) {
    if str, ok := data.(string); ok {
        fmt.Println("String data:", str)
    } else if num, ok := data.(int); ok {
        fmt.Println("Number data:", num)
    }
}
```

<!-- full-library-explanation -->
## 方法接收者与接口满足条件

前置是结构体、指针和函数。方法是带接收者的函数；指针接收者允许修改原对象。编译器对可寻址变量的方法调用可提供取址便利，但把值放进接口时仍按方法集检查，不会自动把 T 转成 *T。结构体字段并非“默认私有”：首字母大写的标识符会从包中导出，首字母小写的标识符只在包内可见。

完整程序保存为 main.go 后运行：

<!-- go-rust-php-twelfth-case: go-pointer-method-set -->
```go
package main
import "fmt"
type Counter struct { n int }
func (c *Counter) Increment() { c.n++ }
type Incrementer interface { Increment() }
func main() {
    c := Counter{}
    var worker Incrementer = &c
    worker.Increment()
    fmt.Println(c.n)
}
```

输出 1。练习：把 &c 改成 c，编译应失败，因为 Increment 属于 *Counter 的方法集。结构体嵌入用于组合和方法提升，不等于具有虚方法覆盖语义的类继承；出现同名成员时要明确选择访问路径。

## 🔗 相关资源

- **深入学习**: [basics/05-functions-methods.md](../../basics/05-functions-methods.md)
- **相关文档**: [reference/language-concepts/04-go-data-types.md](04-go-data-types.md)
- **实践参考**: [frameworks/01-gin-framework-basics.md](../../frameworks/01-gin-framework-basics.md)

---

**更新日志**: 2026年9月 - 创建Go面向对象概念速查手册


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
