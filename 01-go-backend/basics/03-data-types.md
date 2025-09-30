# Go 数据类型详解 - 从PHP视角理解

## 📚 概述

Go的数据类型系统与PHP有显著差异。作为静态类型语言，Go在编译时就确定了所有变量的类型，这提供了更好的性能和类型安全性。理解Go的数据类型对于PHP开发者至关重要。

### 🎯 学习目标
- 掌握Go的基本数据类型和特点
- 理解Go的类型推断和类型转换
- 学会Go的复合数据类型使用
- 熟悉Go的类型系统与PHP的差异

## 🔄 Go vs PHP 数据类型对比

### 基本数据类型对比

| PHP | Go | 说明 |
|-----|-----|------|
| `$name = "张三"` | `var name string = "张三"` | PHP动态类型，Go静态类型 |
| `$age = 25` | `var age int = 25` | PHP自动转换，Go明确类型 |
| `$price = 19.99` | `var price float64 = 19.99` | PHP统一浮点数，Go区分精度 |
| `$isActive = true` | `var isActive bool = true` | 语法相似，Go类型明确 |

### 类型声明对比

#### PHP 类型声明
```php
<?php
// PHP 7+ 类型声明
function greetUser(string $name, int $age): string {
    return "Hello {$name}, age {$age}";
}

// PHP联合类型 (PHP 8+)
function processValue(int|float|string $value): void {
    // 处理多种类型
}

// PHP混合类型
function processMixed(mixed $data): mixed {
    return $data;
}
```

#### Go 类型声明
```go
// 明确的类型声明
func greetUser(name string, age int) string {
    return fmt.Sprintf("Hello %s, age %d", name, age)
}

// 自定义类型
type Age int
type Name string
type Price float64

func processUser(name Name, age Age) string {
    return fmt.Sprintf("User: %s, Age: %d", name, age)
}
```

## 📝 Go 数据类型详解

### 1. 基本数据类型

#### 整数类型
```go
// 有符号整数
var age int = 25                    // 根据系统架构决定位数
var small int8 = 127                // 8位有符号整数 (-128 到 127)
var medium int16 = 32767            // 16位有符号整数 (-32768 到 32767)
var large int32 = 2147483647        // 32位有符号整数
var huge int64 = 9223372036854775807 // 64位有符号整数

// 无符号整数
var count uint = 100                 // 根据系统架构决定位数
var byteCount byte = 255            // uint8的别名 (0 到 255)
var smallCount uint16 = 65535       // 16位无符号整数 (0 到 65535)
var mediumCount uint32 = 4294967295 // 32位无符号整数
var largeCount uint64 = 18446744073709551615 // 64位无符号整数

// 特殊整数类型
var ptr uintptr = 0x7ffd12345678   // 足够存储指针的整数
var runeChar rune = 'A'             // int32的别名，表示Unicode码点
```

#### 浮点数类型
```go
// 32位浮点数
var temperature float32 = 36.6
var pi32 float32 = 3.1415926535

// 64位浮点数 (推荐使用)
var price float64 = 19.99
var pi64 float64 = 3.141592653589793

// 浮点数运算
var result float64 = 10.0 / 3.0     // 3.3333333333333335
var precise float64 = float64(10) / float64(3) // 更精确的运算
```

#### 字符串类型
```go
// 基本字符串
var name string = "张三"
var message string = "Hello, World!"

// 多行字符串
var longMessage string = `这是一个多行字符串
可以包含换行符
不需要转义字符`

// 字符串操作
var fullName string = name + " 李四"           // 字符串拼接
var formatted string = fmt.Sprintf("Name: %s, Age: %d", name, 25) // 格式化

// 字符串长度 (UTF-8字符数)
var length int = len(name)                    // 字节数
var charCount int = utf8.RuneCountInString(name) // 字符数

// 字符串切片
var substring string = name[1:3]              // 获取子字符串
```

#### 布尔类型
```go
// 布尔值
var isActive bool = true
var isComplete bool = false

// 布尔运算
var result bool = isActive && isComplete      // 逻辑与
var result2 bool = isActive || isComplete     // 逻辑或
var result3 bool = !isActive                  // 逻辑非

// 条件表达式
var status string
if isActive {
    status = "active"
} else {
    status = "inactive"
}

// 简洁的布尔表达式
status = map[bool]string{true: "active", false: "inactive"}[isActive]
```

### 2. 复合数据类型

#### 数组类型
```go
// 固定长度数组
var numbers [5]int = [5]int{1, 2, 3, 4, 5}
var names [3]string = [3]string{"张三", "李四", "王五"}

// 数组长度和容量
var length int = len(numbers)    // 5
var capacity int = cap(numbers)   // 5

// 数组访问和修改
numbers[0] = 10                  // 修改第一个元素
var firstNum int = numbers[0]     // 获取第一个元素

// 多维数组
var matrix [3][3]int = [3][3]int{
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9},
}

// 数组遍历
for i, num := range numbers {
    fmt.Printf("Index %d: %d\n", i, num)
}
```

#### 切片类型
```go
// 切片创建 (动态长度)
var fruits []string = []string{"苹果", "香蕉", "橙子"}
var numbers []int = []int{1, 2, 3, 4, 5}

// 切片操作
fruits = append(fruits, "葡萄")    // 添加元素
fruits = append(fruits, "西瓜", "菠萝") // 添加多个元素

// 切片子集
var subset []string = fruits[1:3]   // 从索引1到3的子集
var firstTwo []string = fruits[:2]  // 前两个元素
var lastTwo []string = fruits[2:]   // 从索引2到末尾

// 切片长度和容量
var length int = len(fruits)        // 当前元素数量
var capacity int = cap(fruits)     // 底层数组容量

// 切片预分配
var largeSlice []int = make([]int, 0, 1000) // 预分配容量1000

// 切片复制
var copySlice []int = make([]int, len(numbers))
copy(copySlice, numbers)           // 复制元素

// 切片删除元素
fruits = append(fruits[:1], fruits[2:]...) // 删除索引1的元素
```

#### 映射类型
```go
// 映射创建
var person map[string]interface{} = map[string]interface{}{
    "name":  "张三",
    "age":   25,
    "email": "zhangsan@example.com",
}

// 映射操作
person["phone"] = "13800138000"    // 添加键值对
delete(person, "email")             // 删除键值对

// 映射查找
if email, exists := person["email"]; exists {
    fmt.Printf("Email: %s\n", email)
} else {
    fmt.Println("Email not found")
}

// 映射遍历
for key, value := range person {
    fmt.Printf("%s: %v\n", key, value)
}

// 类型化映射
var scores map[string]int = map[string]int{
    "math":    90,
    "english": 85,
    "science": 92,
}

// 映射的嵌套
var nestedMap map[string]map[string]int = map[string]map[string]int{
    "student1": {"math": 90, "english": 85},
    "student2": {"math": 85, "english": 92},
}
```

#### 结构体类型
```go
// 基本结构体
type User struct {
    ID       int
    Name     string
    Email    string
    Age      int
    Active   bool
}

// 结构体实例化
var user User = User{
    ID:     1,
    Name:   "张三",
    Email:  "zhangsan@example.com",
    Age:    25,
    Active: true,
}

// 结构体指针
var userPtr *User = &user
userPtr.Name = "李四"               // 通过指针修改字段

// 结构体方法
func (u User) Greet() string {
    return fmt.Sprintf("Hello, %s!", u.Name)
}

func (u *User) UpdateEmail(newEmail string) {
    u.Email = newEmail
}

// 匿名结构体
var anonymous struct {
    Name string
    Age  int
} = struct{
    Name string
    Age  int
}{
    Name: "临时用户",
    Age:  30,
}

// 嵌套结构体
type Address struct {
    Street  string
    City    string
    Country string
}

type Person struct {
    Name    string
    Age     int
    Address Address
}

// 嵌套结构体使用
var person Person = Person{
    Name: "王五",
    Age:  35,
    Address: Address{
        Street:  "123 Main St",
        City:    "Beijing",
        Country: "China",
    },
}
```

### 3. 指针类型

#### 指针基础
```go
// 指针声明和使用
var age int = 25
var agePtr *int = &age             // 获取age的指针

fmt.Printf("Age: %d\n", age)       // 输出: 25
fmt.Printf("Age Ptr: %d\n", *agePtr) // 输出: 25

// 通过指针修改值
*agePtr = 30
fmt.Printf("New Age: %d\n", age)   // 输出: 30

// 指针作为函数参数
func increment(num *int) {
    *num++
}

var counter int = 0
increment(&counter)                 // 传递指针
fmt.Printf("Counter: %d\n", counter) // 输出: 1
```

#### 指针与结构体
```go
// 结构体指针
var user *User = &User{
    ID:     1,
    Name:   "张三",
    Email:  "zhangsan@example.com",
    Age:    25,
    Active: true,
}

// 通过指针访问字段
fmt.Printf("User Name: %s\n", user.Name)
user.Name = "李四"                  // 修改字段

// 指针接收器方法
func (u *User) Deactivate() {
    u.Active = false
}

user.Deactivate()                   // 调用指针方法
```

### 4. 函数类型

#### 函数作为类型
```go
// 函数类型定义
type MathFunc func(int, int) int

// 函数变量
var add MathFunc = func(a, b int) int {
    return a + b
}

var subtract MathFunc = func(a, b int) int {
    return a - b
}

// 函数作为参数
func calculate(a, b int, operation MathFunc) int {
    return operation(a, b)
}

// 使用函数
var result int = calculate(10, 5, add)    // 15
result = calculate(10, 5, subtract)       // 5

// 函数作为返回值
func getOperation(op string) MathFunc {
    switch op {
    case "add":
        return func(a, b int) int { return a + b }
    case "subtract":
        return func(a, b int) int { return a - b }
    default:
        return func(a, b int) int { return 0 }
    }
}
```

### 5. 接口类型

#### 接口定义
```go
// 基本接口
type Writer interface {
    Write([]byte) (int, error)
}

type Reader interface {
    Read([]byte) (int, error)
}

// 实现接口
type FileWriter struct {
    filename string
}

func (fw FileWriter) Write(data []byte) (int, error) {
    // 实现写入逻辑
    return len(data), nil
}

// 接口使用
func writeData(w Writer, data []byte) error {
    _, err := w.Write(data)
    return err
}

// 空接口
func processAny(value interface{}) {
    switch v := value.(type) {
    case string:
        fmt.Printf("String: %s\n", v)
    case int:
        fmt.Printf("Integer: %d\n", v)
    default:
        fmt.Printf("Unknown type: %T\n", v)
    }
}
```

## 🧪 类型转换和类型推断

### 类型转换
```go
// 基本类型转换
var intNum int = 42
var floatNum float64 = float64(intNum)
var stringNum string = strconv.Itoa(intNum)

// 字符串转换
var str string = "123"
var num int = 0
var err error

num, err = strconv.Atoi(str)
if err != nil {
    fmt.Printf("转换失败: %v\n", err)
}

// 浮点数转换
var floatStr string = "3.14"
var floatValue float64
floatValue, err = strconv.ParseFloat(floatStr, 64)
if err != nil {
    fmt.Printf("转换失败: %v\n", err)
}
```

### 类型推断
```go
// 使用 := 进行类型推断
name := "张三"                      // 推断为string
age := 25                           // 推断为int
price := 19.99                      // 推断为float64
isActive := true                    // 推断为bool

// 函数返回值类型推断
func getUser() (string, int) {
    return "张三", 25
}

userName, userAge := getUser()      // 推断为string和int
```

## 📋 实践练习

### 练习1: 数据类型转换
```go
package main

import (
    "fmt"
    "strconv"
)

func main() {
    // 字符串到数字的转换
    var strNum string = "42"
    var num int

    num, err := strconv.Atoi(strNum)
    if err != nil {
        fmt.Printf("转换失败: %v\n", err)
        return
    }

    fmt.Printf("字符串 '%s' 转换为数字: %d\n", strNum, num)

    // 数字到字符串的转换
    var convertedStr string = strconv.Itoa(num)
    fmt.Printf("数字 %d 转换回字符串: '%s'\n", num, convertedStr)
}
```

### 练习2: 结构体和方法
```go
package main

import "fmt"

type Product struct {
    ID    int
    Name  string
    Price float64
}

// 构造函数
func NewProduct(id int, name string, price float64) *Product {
    return &Product{
        ID:    id,
        Name:  name,
        Price: price,
    }
}

// 方法
func (p Product) GetInfo() string {
    return fmt.Sprintf("产品: %s, 价格: %.2f", p.Name, p.Price)
}

func (p *Product) ApplyDiscount(discount float64) {
    p.Price = p.Price * (1 - discount/100)
}

func main() {
    product := NewProduct(1, "iPhone 15", 6999.00)

    fmt.Println(product.GetInfo())

    product.ApplyDiscount(10) // 打9折
    fmt.Println(product.GetInfo())
}
```

### 练习3: 切片操作
```go
package main

import "fmt"

func main() {
    // 创建切片
    numbers := []int{1, 2, 3, 4, 5}

    // 添加元素
    numbers = append(numbers, 6, 7, 8)

    // 切片操作
    fmt.Println("原始切片:", numbers)
    fmt.Println("前3个元素:", numbers[:3])
    fmt.Println("第2到第4个元素:", numbers[1:4])

    // 删除元素
    numbers = append(numbers[:1], numbers[2:]...)
    fmt.Println("删除第2个元素后:", numbers)

    // 切片复制
    copySlice := make([]int, len(numbers))
    copy(copySlice, numbers)
    fmt.Println("复制的切片:", copySlice)
}
```

## 📋 检查清单

- [ ] 理解Go的基本数据类型和范围
- [ ] 掌握Go的复合数据类型使用
- [ ] 学会Go的指针类型和内存管理
- [ ] 理解Go的类型转换和类型推断
- [ ] 掌握结构体和方法的定义
- [ ] 学会接口的概念和实现
- [ ] 能够使用切片和映射进行数据处理
- [ ] 理解Go类型系统与PHP的差异

## 🚀 下一步

掌握数据类型后，你可以继续学习：
- **控制流程**: 条件语句、循环语句、跳转语句
- **函数深入**: 高级函数特性、闭包、递归
- **并发编程**: Goroutine和Channel
- **标准库**: 常用包的使用方法

---

**学习提示**: Go的类型系统比PHP更严格，但这也意味着更少的运行时错误。多练习类型转换和复合数据类型的使用，你会逐渐体会到Go类型安全的优势。

*最后更新: 2025年9月*