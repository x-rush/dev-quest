# 第一个Go程序 - 从零开始

> **文档简介**: 学习编写、运行和理解你的第一个Go程序，掌握Go程序的基本结构和运行方式

> **目标读者**: Go初学者，希望快速上手编写第一个Go程序的学习者

> **前置知识**: Go环境已配置完成，了解基本编程概念

> **预计时长**: 1-2小时学习 + 实践

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `basics/programming-fundamentals` |
| **难度** | ⭐ (1/5) |
| **标签** | `#第一个程序` `#HelloWorld` `#基础语法` `#程序结构` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

通过本文档学习，您将能够：
- 编写并运行第一个Go程序
- 理解Go程序的基本结构
- 掌握Go程序的编译和运行方式
- 学会使用Go命令行工具
- 理解Go包和模块的基本概念

## 🚀 编写第一个Go程序

### 1. 创建程序文件

创建你的第一个Go程序文件 `hello.go`：

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
    fmt.Println("欢迎来到Go语言的世界!")
}
```

### 2. 程序结构解析

让我们逐行分析这个程序：

```go
// 包声明 - 定义这个文件属于哪个包
package main

// 导入包 - 导入需要使用的包
import "fmt"

// 主函数 - 程序的入口点
func main() {
    // 调用fmt包的Println函数
    fmt.Println("Hello, World!")
    fmt.Println("欢迎来到Go语言的世界!")
}
```

#### 关键概念解释：

- **`package main`**:
  - 每个Go程序都必须属于一个包
  - `main`包是特殊的，表示这是一个可执行程序
  - 只有main包中的main函数才能作为程序入口

- **`import "fmt"`**:
  - 导入标准库中的`fmt`包
  - `fmt`包提供格式化输入输出功能
  - 用于打印文本到控制台

- **`func main()`**:
  - 程序的主入口函数
  - 程序从这里开始执行
  - 当main函数返回时，程序结束

- **`fmt.Println()`**:
  - 打印一行文本到控制台
  - 自动在末尾添加换行符

## 🔧 运行Go程序

### 方法1: 直接运行
```bash
# 直接运行Go文件
go run hello.go
```

输出：
```
Hello, World!
欢迎来到Go语言的世界!
```

### 方法2: 先编译后运行
```bash
# 编译Go程序
go build hello.go

# 运行生成的可执行文件
./hello
```

在Windows上：
```bash
# 编译
go build hello.go

# 运行
hello.exe
```

### 方法3: 使用模块
```bash
# 初始化Go模块
go mod init hello-world

# 运行程序
go run hello.go
```

## 📝 程序进阶练习

### 练习1: 添加变量
```go
package main

import "fmt"

func main() {
    // 声明变量
    name := "张三"
    age := 25
    city := "北京"

    // 打印个人信息
    fmt.Println("个人信息:")
    fmt.Printf("姓名: %s\n", name)
    fmt.Printf("年龄: %d\n", age)
    fmt.Printf("城市: %s\n", city)

    // 计算并显示明年年龄
    nextAge := age + 1
    fmt.Printf("明年年龄: %d\n", nextAge)
}
```

### 练习2: 使用函数
```go
package main

import "fmt"

// 定义一个简单的函数
func greet(name string) {
    fmt.Printf("你好, %s!\n", name)
}

// 带返回值的函数
func add(a, b int) int {
    return a + b
}

func main() {
    // 调用greet函数
    greet("小明")
    greet("小红")

    // 调用add函数
    result := add(10, 20)
    fmt.Printf("10 + 20 = %d\n", result)
}
```

### 练习3: 条件判断
```go
package main

import "fmt"

func checkAge(age int) {
    if age >= 18 {
        fmt.Printf("%d岁是成年人\n", age)
    } else {
        fmt.Printf("%d岁是未成年人\n", age)
    }
}

func main() {
    // 测试不同年龄
    checkAge(16)
    checkAge(18)
    checkAge(25)

    // 用户输入年龄
    var userAge int
    fmt.Print("请输入你的年龄: ")
    fmt.Scanln(&userAge)

    checkAge(userAge)
}
```

## 🛠️ 常用Go命令

### 基本命令
```bash
# 运行Go程序
go run filename.go

# 编译Go程序
go build filename.go

# 运行测试
go test

# 格式化代码
go fmt filename.go

# 检查代码错误
go vet filename.go
```

### 模块命令
```bash
# 初始化模块
go mod init module-name

# 添加依赖
go get package-name

# 整理依赖
go mod tidy

# 查看依赖
go mod list
```

## 📊 程序调试技巧

### 1. 使用fmt调试
```go
package main

import "fmt"

func calculateSum(numbers []int) int {
    sum := 0
    for i, num := range numbers {
        fmt.Printf("处理第%d个数: %d\n", i, num) // 调试输出
        sum += num
    }
    fmt.Printf("总和: %d\n", sum) // 调试输出
    return sum
}

func main() {
    numbers := []int{1, 2, 3, 4, 5}
    result := calculateSum(numbers)
    fmt.Printf("最终结果: %d\n", result)
}
```

### 2. 使用panic调试
```go
package main

import "fmt"

func process(data string) {
    if data == "" {
        panic("数据不能为空") // 程序会在这里停止并显示错误信息
    }
    fmt.Printf("处理数据: %s\n", data)
}

func main() {
    process("Hello")
    // process("") // 这行会触发panic
}
```

## 🎯 实战小项目

### 项目1: 个人信息卡片
```go
package main

import "fmt"

// 定义个人信息结构体
type Person struct {
    Name    string
    Age     int
    City    string
    Hobby   string
}

// 打印个人信息
func printPersonInfo(p Person) {
    fmt.Println("=== 个人信息 ===")
    fmt.Printf("姓名: %s\n", p.Name)
    fmt.Printf("年龄: %d\n", p.Age)
    fmt.Printf("城市: %s\n", p.City)
    fmt.Printf("爱好: %s\n", p.Hobby)
    fmt.Println("================")
}

func main() {
    // 创建个人信息
    me := Person{
        Name:  "张三",
        Age:   28,
        City:  "上海",
        Hobby: "编程",
    }

    // 打印信息
    printPersonInfo(me)

    // 创建朋友信息
    friend := Person{
        Name:  "李四",
        Age:   26,
        City:  "北京",
        Hobby: "阅读",
    }

    printPersonInfo(friend)
}
```

### 项目2: 简单计算器
```go
package main

import "fmt"

// 加法
func add(a, b float64) float64 {
    return a + b
}

// 减法
func subtract(a, b float64) float64 {
    return a - b
}

// 乘法
func multiply(a, b float64) float64 {
    return a * b
}

// 除法
func divide(a, b float64) float64 {
    if b == 0 {
        fmt.Println("错误: 除数不能为0")
        return 0
    }
    return a / b
}

func main() {
    var num1, num2 float64
    var operator string

    fmt.Println("=== 简单计算器 ===")
    fmt.Print("请输入第一个数字: ")
    fmt.Scanln(&num1)

    fmt.Print("请输入运算符 (+, -, *, /): ")
    fmt.Scanln(&operator)

    fmt.Print("请输入第二个数字: ")
    fmt.Scanln(&num2)

    var result float64
    switch operator {
    case "+":
        result = add(num1, num2)
    case "-":
        result = subtract(num1, num2)
    case "*":
        result = multiply(num1, num2)
    case "/":
        result = divide(num1, num2)
    default:
        fmt.Println("错误: 不支持的运算符")
        return
    }

    fmt.Printf("结果: %.2f %s %.2f = %.2f\n", num1, operator, num2, result)
}
```

## 🔍 常见错误和解决方法

### 错误1: 包声明错误
```go
// ❌ 错误
package mainx  // 拼写错误

// ✅ 正确
package main
```

### 错误2: 未使用的导入
```go
// ❌ 错误
package main

import "fmt"     // 导入了但未使用
import "os"      // 导入了但未使用

func main() {
    fmt.Println("Hello")
}

// ✅ 正确
package main

import "fmt"

func main() {
    fmt.Println("Hello")
}
```

### 错误3: 缺少分号（在Go中不需要）
```go
// ❌ 错误 - Go不需要分号
package main

import "fmt";

func main() {
    fmt.Println("Hello");  // 这里不需要分号
}

// ✅ 正确
package main

import "fmt"

func main() {
    fmt.Println("Hello")
}
```

### 错误4: 大小写敏感
```go
// ❌ 错误
package main

import "fmt"

func main() {
    fmt.println("Hello")  // 应该是Println（大写P）
}

// ✅ 正确
package main

import "fmt"

func main() {
    fmt.Println("Hello")  // 注意大小写
}
```

## 📈 下一步学习建议

完成第一个Go程序后，建议按以下顺序继续学习：

1. **变量和常量** - 学习Go的数据类型和变量声明
2. **函数和方法** - 深入学习函数定义和调用
3. **控制结构** - 掌握条件语句和循环
4. **错误处理** - 学习Go的错误处理机制
5. **结构体和接口** - 了解Go的面向对象编程

## 🔗 文档交叉引用

### 相关文档
- 📄 **[环境搭建]**: [basics/01-environment-setup.md](01-environment-setup.md) - Go开发环境配置
- 📄 **[变量和常量]**: [basics/03-variables-constants.md](03-variables-constants.md) - Go数据类型和变量
- 📄 **[函数和方法]**: [basics/04-functions-methods.md](04-functions-methods.md) - 函数定义和方法调用

### 参考资源
- 📖 **[Go官方教程]**: https://tour.golang.org/
- 📖 **[Go Playground]**: https://play.golang.org/
- 📖 **[Go官方文档]**: https://golang.org/doc/

## 📝 总结

### 核心要点回顾
1. **程序结构**: 理解package main和import的作用
2. **运行方式**: 掌握go run和go build的区别
3. **基本语法**: 学习函数定义和调用
4. **调试技巧**: 使用fmt包进行简单调试

### 实践练习
- [ ] 成功运行第一个Go程序
- [ ] 修改程序输出自己的信息
- [ ] 创建一个简单的计算器程序
- [ ] 尝试使用不同的数据类型和操作

---

**文档状态**: ✅ 已完成
**最后更新**: 2025年10月
**版本**: v1.0.0

---

> 💡 **学习建议**:
> - 多动手实践，不要只看不练
> - 遇到错误时仔细阅读错误信息
> - 使用Go官方的Tour进行交互式学习
> - 尝试修改示例代码，观察运行结果的变化