# Go 基础语法 - 从PHP视角理解Go

## 📚 概述

Go语言的语法设计简洁明了，但与PHP有很多重要区别。作为PHP开发者，理解这些差异对于快速上手Go至关重要。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `basics/programming-fundamentals` |
| **难度** | ⭐⭐ |
| **标签** | `#基础语法` `#变量` `#函数` `#错误处理` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

### 🎯 学习目标
- 掌握Go的变量声明和类型系统
- 理解Go的函数定义和调用
- 学会Go的错误处理模式
- 熟悉Go的包管理机制

## 🔄 Go vs PHP 语法对比

### 变量声明

#### PHP 变量声明
```php
<?php
// PHP是动态类型语言
$name = "张三";
$age = 25;
$salary = 8500.50;
$is_active = true;

// 类型声明 (PHP 7+)
function greet(string $name): string {
    return "Hello, " . $name;
}
```

#### Go 变量声明
```go
// Go是静态类型语言
var name string = "张三"
var age int = 25
var salary float64 = 8500.50
var isActive bool = true

// 短变量声明 (函数内常用)
name := "张三"           // 自动推断为string类型
age := 25                // 自动推断为int类型
salary := 8500.50        // 自动推断为float64类型
isActive := true         // 自动推断为bool类型

// 函数定义
func greet(name string) string {
    return "Hello, " + name
}
```

### 关键语法差异

#### 1. 变量声明方式

| PHP | Go |
|-----|-----|
| `$name = "value";` | `var name string = "value"` 或 `name := "value"` |
| 无需声明类型 | 必须指定类型或类型推断 |
| 变量名以$开头 | 变量名不以$开头 |

#### 2. 字符串拼接

```php
// PHP字符串拼接
$greeting = "Hello, " . $name;
$greeting = "Hello, {$name}";  // 插值语法
```

```go
// Go字符串拼接
greeting := "Hello, " + name
greeting := fmt.Sprintf("Hello, %s", name)  // 格式化
```

#### 3. 数组和切片

```php
// PHP数组
$numbers = [1, 2, 3, 4, 5];
$names = ["张三", "李四", "王五"];
$person = ["name" => "张三", "age" => 25];
```

```go
// Go数组 (固定长度)
var numbers [5]int = [5]int{1, 2, 3, 4, 5}

// Go切片 (动态长度)
numbers := []int{1, 2, 3, 4, 5}
names := []string{"张三", "李四", "王五"}

// Go映射 (类似PHP关联数组)
person := map[string]interface{}{
    "name": "张三",
    "age":  25,
}
```

## 📝 Go 基础语法详解

### 1. 变量和常量

#### 变量声明
```go
// 标准声明
var username string
var age int
var isActive bool

// 声明并初始化
var username string = "developer"
var age int = 30
var isActive bool = true

// 批量声明
var (
    username string = "developer"
    age      int    = 30
    isActive bool   = true
)

// 短变量声明 (只能在函数内使用)
username := "developer"
age := 30
isActive := true
```

#### 常量声明
```go
// 常量使用const关键字
const PI = 3.14159
const APP_NAME = "MyGoApp"
const MAX_USERS = 1000

// 批量常量声明
const (
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_PENDING = "pending"
)
```

### 2. 数据类型

#### 基本数据类型
```go
// 整数类型
var age int = 25                    // 有符号整数
var uintAge uint = 25               // 无符号整数
var score int32 = 90                // 32位整数
var bigNumber int64 = 999999999999 // 64位整数

// 浮点数类型
var price float64 = 19.99           // 64位浮点数
var temperature float32 = 36.5      // 32位浮点数

// 字符串类型
var name string = "张三"
var message string = `多行字符串
支持换行和格式化`

// 布尔类型
var isAvailable bool = true

// 字符类型 (Go中字符使用rune类型)
var grade rune = 'A'
```

#### 复合数据类型
```go
// 数组 (固定长度)
var numbers [5]int = [5]int{1, 2, 3, 4, 5}

// 切片 (动态长度)
var fruits []string = []string{"苹果", "香蕉", "橙子"}
fruits = append(fruits, "葡萄")  // 添加元素

// 映射 (类似PHP关联数组)
var person map[string]interface{}
person = map[string]interface{}{
    "name": "张三",
    "age":  25,
    "email": "zhangsan@example.com",
}

// 结构体 (类似PHP类)
type User struct {
    ID       int
    Name     string
    Email    string
    Age      int
    Active   bool
}

var user User = User{
    ID:     1,
    Name:   "张三",
    Email:  "zhangsan@example.com",
    Age:    25,
    Active: true,
}
```

### 3. 函数定义

#### 基本函数
```go
// 基本函数定义
func add(a int, b int) int {
    return a + b
}

// 多个返回值
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("除数不能为零")
    }
    return a / b, nil
}

// 命名返回值
func calculate(a, b int) (sum int, product int) {
    sum = a + b
    product = a * b
    return  // 自动返回命名的变量
}

// 可变参数函数
func sum(numbers ...int) int {
    total := 0
    for _, num := range numbers {
        total += num
    }
    return total
}

// 闭包函数
func multiplier(factor int) func(int) int {
    return func(x int) int {
        return x * factor
    }
}
```

### 4. 错误处理

#### Go的错误处理模式
```go
import (
    "fmt"
    "os"
)

// Go使用显式错误处理，而不是异常
func readFile(filename string) (string, error) {
    data, err := os.ReadFile(filename)
    if err != nil {
        return "", fmt.Errorf("读取文件失败: %v", err)
    }
    return string(data), nil
}

// 使用函数
func main() {
    content, err := readFile("example.txt")
    if err != nil {
        fmt.Printf("错误: %v\n", err)
        return
    }
    fmt.Printf("文件内容: %s\n", content)
}
```

#### 与PHP异常处理对比
```php
// PHP异常处理
try {
    $content = file_get_contents("example.txt");
    echo "文件内容: " . $content;
} catch (Exception $e) {
    echo "错误: " . $e->getMessage();
}
```

### 5. 包管理

#### 包的导入
```go
// 单个包导入
import "fmt"

// 多个包导入
import (
    "fmt"
    "os"
    "strings"
)

// 包的别名
import (
    str "strings"  // 给strings包起别名
)

// 包的初始化
import _ "encoding/json"  // 只执行包的init函数，不使用包内容
```

#### 包的可见性
```go
// 大写字母开头的标识符是公开的 (public)
func PublicFunction() {
    // 可以在包外访问
}

// 小写字母开头的标识符是私有的 (private)
func privateFunction() {
    // 只能在包内访问
}

type PublicStruct struct {
    PublicField  string
    privateField string  // 私有字段
}
```

## 🧪 实践练习

### 练习1: 基础语法转换
```go
// 将PHP代码转换为Go代码
// PHP版本:
<?php
$user = ["name" => "张三", "age" => 25, "email" => "zhangsan@example.com"];
$users = [
    ["name" => "张三", "age" => 25],
    ["name" => "李四", "age" => 30]
];

function greetUser($user) {
    return "Hello, " . $user["name"];
}

echo greetUser($user);
?>

// Go版本:
package main

import "fmt"

type User struct {
    Name  string
    Age   int
    Email string
}

func main() {
    user := User{
        Name:  "张三",
        Age:   25,
        Email: "zhangsan@example.com",
    }

    users := []User{
        {Name: "张三", Age: 25},
        {Name: "李四", Age: 30},
    }

    greeting := greetUser(user)
    fmt.Println(greeting)
}

func greetUser(user User) string {
    return "Hello, " + user.Name
}
```

### 练习2: 函数和错误处理
```go
package main

import (
    "fmt"
    "strconv"
)

func stringToInt(s string) (int, error) {
    return strconv.Atoi(s)
}

func main() {
    // 成功转换
    if num, err := stringToInt("123"); err == nil {
        fmt.Printf("转换成功: %d\n", num)
    } else {
        fmt.Printf("转换失败: %v\n", err)
    }

    // 失败转换
    if num, err := stringToInt("abc"); err == nil {
        fmt.Printf("转换成功: %d\n", num)
    } else {
        fmt.Printf("转换失败: %v\n", err)
    }
}
```

## 📋 检查清单

- [ ] 理解Go的变量声明方式 (var和:=)
- [ ] 掌握Go的基本数据类型
- [ ] 学会Go的函数定义和调用
- [ ] 理解Go的错误处理模式
- [ ] 掌握包的导入和使用
- [ ] 能够将简单PHP代码转换为Go代码
- [ ] 理解Go的可见性规则

## 🚀 下一步

掌握基础语法后，你可以继续学习：
- **数据结构深入**: 切片、映射、结构体的高级用法
- **控制流程**: 条件语句、循环语句、跳转语句
- **面向对象编程**: Go的OOP实现方式
- **标准库**: 常用包的使用方法

---

**学习提示**: Go的语法比PHP更严格，但这也意味着更少的运行时错误。多写代码，熟悉Go的语法规则，你会逐渐喜欢上Go的简洁和高效。

*最后更新: 2025年9月*