# 变量、常量和基础数据类型

> **文档简介**: 全面掌握Go语言的变量声明、常量定义和基础数据类型，理解Go的静态类型系统

> **目标读者**: Go初学者，需要掌握Go基础语法的学习者

> **前置知识**: 已完成第一个Go程序，了解基本程序结构

> **预计时长**: 2-3小时学习 + 练习

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `basics/programming-fundamentals` |
| **难度** | ⭐⭐ (2/5) |
| **标签** | `#变量` `#常量` `#数据类型` `#类型声明` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

通过本文档学习，您将能够：
- 掌握Go变量的声明和初始化方式
- 理解Go常量的定义和使用
- 熟悉Go的基础数据类型
- 学会类型推断和类型转换
- 理解Go的静态类型系统特点

## 📝 变量声明和初始化

### 1. 基本变量声明

Go提供多种变量声明方式：

#### 方式1: 标准声明
```go
// var 变量名 类型 = 值
var name string = "张三"
var age int = 25
var height float64 = 175.5
var isStudent bool = true
```

#### 方式2: 类型推断
```go
// var 变量名 = 值 (编译器自动推断类型)
var name = "张三"        // 自动推断为string
var age = 25            // 自动推断为int
var height = 175.5      // 自动推断为float64
var isStudent = true    // 自动推断为bool
```

#### 方式3: 短变量声明(函数内)
```go
// 变量名 := 值 (只能在函数内使用)
name := "李四"
age := 30
height := 180.0
isStudent := false
```

### 2. 批量声明

```go
// 方式1: 批量标准声明
var (
    username string = "admin"
    password string = "123456"
    loginCount int = 0
    isActive bool = true
)

// 方式2: 多变量声明
var x, y, z int = 1, 2, 3
var name, age = "王五", 28

// 方式3: 短变量批量声明
name, city, country := "赵六", "深圳", "中国"
```

### 3. 零值

Go中每个变量都有零值：

```go
package main

import "fmt"

func main() {
    // 声明变量但不初始化
    var s string
    var i int
    var f float64
    var b bool
    var p *int

    fmt.Printf("string零值: %q (长度: %d)\n", s, len(s))  // "" (长度: 0)
    fmt.Printf("int零值: %d\n", i)                        // 0
    fmt.Printf("float64零值: %f\n", f)                    // 0.000000
    fmt.Printf("bool零值: %t\n", b)                       // false
    fmt.Printf("指针零值: %v\n", p)                       // <nil>
}
```

## 🔒 常量定义

### 1. 常量声明

常量使用`const`关键字声明：

```go
// 单个常量
const PI = 3.14159
const APP_NAME = "MyApp"
const MAX_USERS = 1000

// 批量常量
const (
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_PENDING = "pending"
)

// 常量组(如果省略值，会沿用前一个值)
const (
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
)
```

### 2. iota枚举

`iota`是Go的常量生成器：

```go
package main

import "fmt"

// 定义级别枚举
const (
    LevelUnknown = iota  // 0
    LevelLow            // 1
    LevelMedium         // 2
    LevelHigh           // 3
    LevelCritical       // 4
)

// 带计算的表达式
const (
    _ = iota             // 忽略0
    KB = 1 << (10 * iota) // 1 << 10 = 1024
    MB = 1 << (10 * iota) // 1 << 20 = 1048576
    GB = 1 << (10 * iota) // 1 << 30 = 1073741824
)

func main() {
    fmt.Printf("LevelLow: %d\n", LevelLow)
    fmt.Printf("KB: %d\n", KB)
    fmt.Printf("MB: %d\n", MB)
    fmt.Printf("GB: %d\n", GB)
}
```

## 📊 基础数据类型

### 1. 布尔类型

```go
var isActive bool = true
var isCompleted bool = false

// 布尔运算
func main() {
    a := true
    b := false

    fmt.Printf("a && b = %t\n", a && b)    // false
    fmt.Printf("a || b = %t\n", a || b)    // true
    fmt.Printf("!a = %t\n", !a)            // false
}
```

### 2. 数值类型

#### 整数类型
```go
// 有符号整数
var i8 int8 = 127          // -128 到 127
var i16 int16 = 32767       // -32768 到 32767
var i32 int32 = 2147483647  // -2147483648 到 2147483647
var i64 int64 = 9223372036854775807  // -9.22e18 到 9.22e18

// 无符号整数
var ui8 uint8 = 255          // 0 到 255
var ui16 uint16 = 65535      // 0 到 65535
var ui32 uint32 = 4294967295  // 0 到 4294967295
var ui64 uint64 = 18446744073709551615  // 0 到 1.84e19

// 平台相关类型
var i int = 42              // 32位或64位，取决于平台
var u uint = 42             // 32位或64位无符号整数
var ptr uintptr = 0x123456  // 存放指针的无符号整数
```

#### 浮点数类型
```go
var f32 float32 = 3.14159    // IEEE-754 32位浮点数
var f64 float64 = 2.718281828 // IEEE-754 64位浮点数

// 浮点数运算
func main() {
    var a float64 = 3.14
    var b float64 = 2.71

    sum := a + b
    fmt.Printf("%.2f + %.2f = %.2f\n", a, b, sum)  // 3.14 + 2.71 = 5.85
}
```

#### 复数类型
```go
var c64 complex64 = 3 + 4i    // 32位实数和虚数
var c128 complex128 = 1 + 2i   // 64位实数和虚数

func main() {
    c := 3 + 4i
    fmt.Printf("实部: %f, 虚部: %f\n", real(c), imag(c))  // 实部: 3.000000, 虚部: 4.000000
    fmt.Printf("模: %f\n", cmplx.Abs(c))                   // 模: 5.000000
}
```

### 3. 字符串类型

```go
// 字符串声明
var s1 string = "Hello, World!"
s2 := "Go语言"

// 多行字符串
s3 := `这是一个
多行字符串
可以包含换行符`

// 字符串操作
func main() {
    s := "Hello"

    // 字符串连接
    greeting := s + ", World!"
    fmt.Println(greeting)  // Hello, World!

    // 字符串长度
    fmt.Printf("长度: %d\n", len(s))  // 长度: 5

    // 字符串索引
    fmt.Printf("第一个字符: %c\n", s[0])  // 第一个字符: H

    // 字符串切片
    fmt.Printf("子串: %s\n", s[1:3])     // 子串: el
}
```

### 4. 字符类型

```go
// byte是uint8的别名，用于ASCII字符
var c1 byte = 'A'  // 65

// rune是int32的别名，用于Unicode字符
var c2 rune = '中'  // Unicode码点

func main() {
    // 遍历字符串的字符
    s := "Hello世界"

    fmt.Println("按字节遍历:")
    for i := 0; i < len(s); i++ {
        fmt.Printf("%d: %c\n", i, s[i])
    }

    fmt.Println("\n按字符遍历:")
    for i, r := range s {
        fmt.Printf("%d: %c (码点: %d)\n", i, r, r)
    }
}
```

## 🔄 类型转换

### 1. 显式类型转换

Go是强类型语言，需要显式转换：

```go
func main() {
    var i int = 42
    var f float64 = 3.14

    // 整数转浮点数
    f2 := float64(i)
    fmt.Printf("int %d 转为 float64: %f\n", i, f2)

    // 浮点数转整数(会丢失小数部分)
    i2 := int(f)
    fmt.Printf("float64 %f 转为 int: %d\n", f, i2)

    // 不同整数类型间转换
    var i16 int16 = 1000
    var i8 int8 = int8(i16)  // 可能溢出，需要小心
    fmt.Printf("int16 %d 转为 int8: %d\n", i16, i8)
}
```

### 2. 字符串转换

```go
package main

import (
    "fmt"
    "strconv"
)

func main() {
    // 数字转字符串
    i := 42
    f := 3.14
    b := true

    si := strconv.Itoa(i)           // int转string
    sf := strconv.FormatFloat(f, 'f', 2, 64)  // float64转string
    sb := strconv.FormatBool(b)       // bool转string

    fmt.Printf("数字转字符串: %s, %s, %s\n", si, sf, sb)

    // 字符串转数字
    s1 := "123"
    s2 := "3.14"
    s3 := "true"

    i2, _ := strconv.Atoi(s1)        // string转int
    f2, _ := strconv.ParseFloat(s2, 64)  // string转float64
    b2, _ := strconv.ParseBool(s3)   // string转bool

    fmt.Printf("字符串转数字: %d, %f, %t\n", i2, f2, b2)
}
```

## 🎯 实际应用示例

### 示例1: 用户信息管理

```go
package main

import "fmt"

// 定义用户信息结构
type UserInfo struct {
    ID       int
    Username string
    Age      int
    Email    string
    IsActive bool
}

func main() {
    // 创建用户信息
    var user1 UserInfo
    user1.ID = 1
    user1.Username = "zhangsan"
    user1.Age = 25
    user1.Email = "zhangsan@example.com"
    user1.IsActive = true

    // 使用短声明创建第二个用户
    user2 := UserInfo{
        ID:       2,
        Username: "lisi",
        Age:      30,
        Email:    "lisi@example.com",
        IsActive: false,
    }

    // 显示用户信息
    displayUser(user1)
    displayUser(user2)
}

func displayUser(user UserInfo) {
    fmt.Println("=== 用户信息 ===")
    fmt.Printf("ID: %d\n", user.ID)
    fmt.Printf("用户名: %s\n", user.Username)
    fmt.Printf("年龄: %d\n", user.Age)
    fmt.Printf("邮箱: %s\n", user.Email)
    fmt.Printf("状态: %t\n", user.IsActive)
    fmt.Println("================")
}
```

### 示例2: 配置管理

```go
package main

import "fmt"

// 应用配置常量
const (
    APP_NAME    = "GoWebApp"
    APP_VERSION  = "1.0.0"
    MAX_CONNECTIONS = 100

    // 日志级别
    LOG_DEBUG = iota
    LOG_INFO
    LOG_WARN
    LOG_ERROR
)

// 配置结构
type Config struct {
    Host     string
    Port     int
    Debug    bool
    LogLevel int
}

func main() {
    // 使用默认配置
    config := Config{
        Host:     "localhost",
        Port:     8080,
        Debug:    false,
        LogLevel: LOG_INFO,
    }

    // 显示配置信息
    fmt.Printf("应用: %s v%s\n", APP_NAME, APP_VERSION)
    fmt.Printf("最大连接数: %d\n", MAX_CONNECTIONS)
    fmt.Printf("服务器地址: %s:%d\n", config.Host, config.Port)

    // 根据配置调整行为
    if config.Debug {
        fmt.Println("调试模式已启用")
    }

    switch config.LogLevel {
    case LOG_DEBUG:
        fmt.Println("日志级别: DEBUG")
    case LOG_INFO:
        fmt.Println("日志级别: INFO")
    case LOG_WARN:
        fmt.Println("日志级别: WARN")
    case LOG_ERROR:
        fmt.Println("日志级别: ERROR")
    }
}
```

### 示例3: 数据计算

```go
package main

import (
    "fmt"
    "math"
)

// 计算圆的面积和周长
func calculateCircle(radius float64) (area, circumference float64) {
    area = math.Pi * radius * radius
    circumference = 2 * math.Pi * radius
    return
}

func main() {
    // 输入数据
    var radius float64 = 5.0

    // 计算
    area, circumference := calculateCircle(radius)

    // 输出结果
    fmt.Printf("半径: %.2f\n", radius)
    fmt.Printf("面积: %.2f\n", area)
    fmt.Printf("周长: %.2f\n", circumference)

    // 类型转换示例
    areaInt := int(area)
    fmt.Printf("面积(整数部分): %d\n", areaInt)
}
```

## 🔍 常见错误和注意事项

### 1. 类型不匹配错误
```go
// ❌ 错误
var i int = 42
var f float64 = i  // 不能直接赋值，需要类型转换

// ✅ 正确
var i int = 42
var f float64 = float64(i)
```

### 2. 未使用变量错误
```go
// ❌ 错误
func main() {
    var name string = "test"  // 声明但未使用
    fmt.Println("Hello")
}

// ✅ 正确
func main() {
    name := "test"
    fmt.Println("Hello,", name)  // 使用变量
}
```

### 3. 常量类型推断
```go
// ❌ 错误 - 常量必须能在编译时确定值
const x = getNumber()  // getNumber()是函数调用

// ✅ 正确
const x = 42
const y = 3.14
const s = "Hello"
```

## 📈 性能提示

### 1. 选择合适的数据类型
```go
// ✅ 选择合适的类型
var age uint8 = 25        // 年龄用uint8足够(0-255)
var count int = 1000000    // 大数量用int
var price float64 = 19.99  // 金融计算用float64避免精度问题
```

### 2. 避免不必要的类型转换
```go
// ❌ 频繁转换
func process(items []float64) {
    for _, item := range items {
        i := int(item)  // 每次都转换
        // 使用i...
    }
}

// ✅ 保持类型一致
func process(items []int) {
    for _, item := range items {
        // 直接使用item...
    }
}
```

## 🔗 文档交叉引用

### 相关文档
- 📄 **[第一个程序]**: [02-first-program.md](02-first-program.md) - Go程序基础结构
- 📄 **[函数和方法]**: [04-functions-methods.md](04-functions-methods.md) - 函数定义和方法调用
- 📄 **[控制结构]**: [05-control-structures.md](05-control-structures.md) - 条件语句和循环

### 参考资源
- 📖 **[Go数据类型文档]**: https://golang.org/ref/spec#Types
- 📖 **[Go常量文档]**: https://golang.org/ref/spec#Constants
- 📖 **[Go变量文档]**: https://golang.org/ref/spec#Variables

## 📝 总结

### 核心要点回顾
1. **变量声明**: 掌握var、:=和批量声明方式
2. **常量定义**: 理解const和iota的使用
3. **数据类型**: 熟悉基础数据类型和零值
4. **类型转换**: 学会显式类型转换的方法

### 实践练习
- [ ] 练习不同的变量声明方式
- [ ] 创建一个包含多种数据类型的结构体
- [ ] 编写类型转换的示例代码
- [ ] 使用iota创建枚举常量

---

**文档状态**: ✅ 已完成
**最后更新**: 2025年10月
**版本**: v1.0.0

---

> 💡 **学习建议**:
> - 理解Go的静态类型系统，与动态语言进行对比
> - 多练习类型转换，理解转换可能带来的数据丢失
> - 在实际编程中选择合适的数据类型
> - 使用常量提高代码的可读性和维护性